"""Verify a fresh native archive and reconstruct all declared control trajectories."""

import csv
import argparse
from pathlib import Path
import hashlib
import json
import subprocess
import sys
import tarfile

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("evidence", type=Path)
args = parser.parse_args()
root = args.evidence.resolve()
repo = Path(__file__).resolve().parent
frozen = repo / "results/initializer-native-queued-2026-10-20"
command = json.loads((root / "terminal-command.json").read_text())
assert command["status"] == "exited" and command["exit_code"] == 0
receipt = json.loads(command["output"].splitlines()[-1])
archive = root / "native-evidence.tar.gz"
assert archive.stat().st_size == receipt["bytes"]
assert hashlib.sha256(archive.read_bytes()).hexdigest() == receipt["sha256"]
native = root / "native"
native.mkdir()
with tarfile.open(archive) as bundle:
    members = bundle.getmembers()
    assert len({m.name for m in members}) == len(members)
    assert all(m.isfile() or m.isdir() for m in members)
    assert all(
        not Path(m.name).is_absolute() and ".." not in Path(m.name).parts
        for m in members
    )
    hashes = {
        m.name: hashlib.sha256(bundle.extractfile(m).read()).hexdigest()
        for m in members
        if m.isfile()
    }
    bundle.extractall(native, filter="data")
for name, digest in hashes.items():
    assert hashlib.sha256((native / name).read_bytes()).hexdigest() == digest
for name in ["protocol.json", "run_controls.py"]:
    assert (native / name).read_bytes() == (frozen / name).read_bytes()
protocol = json.loads((native / "protocol.json").read_text())
completed = json.loads((native / "completed.json").read_text())
assert [r["variant"] for r in completed] == [r["variant"] for r in protocol["variants"]]
assert all(
    r["exit_code"] == 0 for r in json.loads((native / "commands.json").read_text())
)
assert len(completed) == 9
reports = []
initial_agent_groups = {}
reference_peaks = []
commands = []
for record, variant in zip(completed, protocol["variants"], strict=True):
    name = record["variant"]
    source = native / "variants" / name / "src/main.cu"
    assert hashlib.sha256(source.read_bytes()).hexdigest() == variant["source_sha256"]
    state = native / "runs" / name / "state.csv"
    assert hashlib.sha256(state.read_bytes()).hexdigest() == record["state_sha256"]
    if name == "released":
        assert (
            record["state_sha256"]
            == "4abcce3274d363fd0d0fb648a003cc117b03cc9a917cb095f1153743bbfdf83a"
        )
    if name == "combined_m4_c4_direct":
        assert (
            record["state_sha256"]
            == "dc7da849c4d30b40ddf40fe479640ec894f80ad4287e064db60e7078d16b178b"
        )
    trace = [
        list(map(int, line.split(",")[1:]))
        for line in (native / (name + "-native.log")).read_text().splitlines()
        if line.startswith("RESOLUTION_TRACE,")
    ]
    assert len(trace) == 100 and [row[0] for row in trace] == list(range(100))
    if name != "released":
        assert all(before == 0 and 1 <= after <= 9 for _, before, after in trace)
    else:
        assert trace[0][1] == 0 and all(
            current[1] == previous[2] for previous, current in zip(trace, trace[1:])
        )
    initial = native / "runs" / name / "initial-cells.csv"
    assert (
        hashlib.sha256(initial.read_bytes()).hexdigest()
        == record["initial_cells_sha256"]
    )
    initial_output = root / (name + "-initial-audit.json")
    initial_cmd = [
        sys.executable,
        str(repo / "audit_initializer.py"),
        str(initial),
        str(native / (name + "-native.log")),
        str(initial_output),
        "--metabolism",
        str(variant["metabolism_maximum"]),
        "--capacity",
        str(variant["capacity_maximum"]),
        "--geometry",
        "wrapped" if variant["wrapped_cell_distances"] else "direct",
    ]
    process = subprocess.run(initial_cmd, capture_output=True, text=True, timeout=120)
    commands.append(
        {
            "command": initial_cmd,
            "exit_code": process.returncode,
            "stdout": process.stdout,
            "stderr": process.stderr,
        }
    )
    (root / "native-audit-commands.json").write_text(
        json.dumps(commands, indent=2) + "\n"
    )
    assert process.returncode == 0, (name, process.stderr)
    initial_report = json.loads(initial_output.read_text())
    with initial.open() as stream:
        cells = list(csv.DictReader(stream))
    attributes = [
        {key: row[key] for key in ["id", "x", "y", "status", "sugar", "metabolism"]}
        for row in cells
        if row["status"] == "1"
    ]
    metabolism = variant["metabolism_maximum"]
    if metabolism in initial_agent_groups:
        assert initial_agent_groups[metabolism] == attributes
    else:
        initial_agent_groups[metabolism] = attributes
    peaks = [
        line
        for line in (native / (name + "-native.log")).read_text().splitlines()
        if line.startswith("HOTSPOT,")
    ]
    if name == "released":
        reference_peaks = peaks
    assert peaks == reference_peaks and len(peaks) == 54
    output = root / (name + "-transitions.json")
    cmd = [
        sys.executable,
        str(repo / "audit_state_transitions.py"),
        str(initial),
        str(state),
        str(output),
        "--variant",
        "released" if name == "released" else "combined_with_counter_reset",
        "--initial-audit",
        str(initial_output),
    ]
    process = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    commands.append(
        {
            "command": cmd,
            "exit_code": process.returncode,
            "stdout": process.stdout,
            "stderr": process.stderr,
        }
    )
    (root / "native-audit-commands.json").write_text(
        json.dumps(commands, indent=2) + "\n"
    )
    assert process.returncode == 0, (name, process.stderr)
    report = json.loads(output.read_text())
    reports.append(
        {
            "variant": name,
            "state_sha256": record["state_sha256"],
            "initial_audit": initial_report,
            "resolution_trace": trace,
            "post_step_observations": report["post_step_agent_observations"],
            "moves": report["moves"],
            "deaths": report["deaths"],
            "final": report["observations"][-1],
            "diagonal_moves": sum(r["diagonal_moves"] for r in report["observations"]),
        }
    )
result = {
    "archive": receipt,
    "member_sha256": hashes,
    "variants": reports,
    "scope": "Declared native state accounting conditional on observed destinations; no independent random-choice/conflict-winner reconstruction and no whole-paper completion.",
}
(root / "native-audit.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps(reports, indent=2))
