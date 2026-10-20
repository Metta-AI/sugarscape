"""Verify a fresh native archive and reconstruct all declared control trajectories."""

from pathlib import Path
import hashlib
import json
import subprocess
import sys
import tarfile

root = Path(__file__).resolve().parent
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
    assert (native / name).read_bytes() == (root / name).read_bytes()
protocol = json.loads((native / "protocol.json").read_text())
completed = json.loads((native / "completed.json").read_text())
assert [r["variant"] for r in completed] == [r["variant"] for r in protocol["variants"]]
assert all(
    r["exit_code"] == 0 for r in json.loads((native / "commands.json").read_text())
)
reports = []
commands = []
for record, variant in zip(completed, protocol["variants"], strict=True):
    name = record["variant"]
    source = native / "variants" / name / "src/main.cu"
    assert (
        hashlib.sha256(source.read_bytes()).hexdigest()
        == variant["observed_source_sha256"]
    )
    state = native / "runs" / name / "state.csv"
    assert hashlib.sha256(state.read_bytes()).hexdigest() == record["state_sha256"]
    if name == "released":
        assert (
            record["state_sha256"]
            == "4abcce3274d363fd0d0fb648a003cc117b03cc9a917cb095f1153743bbfdf83a"
        )
    if name == "combined_three_rules":
        assert (
            record["state_sha256"]
            == "2a573063df4331f40d44a2952810c4d73a3474c6ecace75d10921cfe5e7ca17f"
        )
    trace = [
        list(map(int, line.split(",")[1:]))
        for line in (native / (name + "-native.log")).read_text().splitlines()
        if line.startswith("RESOLUTION_TRACE,")
    ]
    assert len(trace) == 100 and [row[0] for row in trace] == list(range(100))
    if variant["counter_reset"]:
        assert all(before == 0 and 1 <= after <= 9 for _, before, after in trace)
    else:
        assert trace[0][1] == 0 and all(
            current[1] == previous[2] for previous, current in zip(trace, trace[1:])
        )
    output = root / (name + "-transitions.json")
    cmd = [
        sys.executable,
        str(
            root.parent.parent
            / "sugarscape-richmond/replications/richmond_2023/audit_state_transitions.py"
        ),
        str(root.parent / "richmond-control-auditor-validation-001/initial.csv"),
        str(state),
        str(output),
        "--variant",
        name,
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
