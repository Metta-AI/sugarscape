"""Verify full native trajectories distinguishing observables from occupied cells."""

import argparse
import csv
import hashlib
import io
import json
from pathlib import Path, PurePosixPath
import tarfile

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("archive", type=Path)
parser.add_argument("receipt", type=Path)
parser.add_argument("output", type=Path)
args = parser.parse_args()
base = Path(__file__).resolve().parent
launch = base / "results/population-semantics-launch-2026-10-19"
receipt = json.loads(args.receipt.read_bytes())["receipt"]
assert args.archive.stat().st_size == receipt["bytes"]
assert hashlib.sha256(args.archive.read_bytes()).hexdigest() == receipt["sha256"]
with tarfile.open(args.archive) as archive:
    contents = {}
    for member in archive.getmembers():
        name = PurePosixPath(member.name)
        assert not name.is_absolute() and ".." not in name.parts
        if member.isdir():
            continue
        assert member.isfile() and str(name) not in contents
        contents[str(name)] = archive.extractfile(member).read()
protocol = json.loads(contents["protocol.json"])
assert protocol == json.loads((launch / "protocol.json").read_bytes())
assert protocol["seed"] == 42 and protocol["steps"] == 1000
assert protocol["repetitions"] == 2 and protocol["capabilities"] == 1
for name, digest in protocol["prepared_sha256"].items():
    assert hashlib.sha256(contents["prepared/" + name]).hexdigest() == digest
with tarfile.open(launch / "cloud-input.tar.gz") as source:
    for name in ["simulate.sh", "bootstrap.sh", "stack-global-config.yaml"]:
        assert contents[name] == source.extractfile(name).read()
assert contents["workflow-exit.txt"].strip() == b"0"
assert contents["exit-code.txt"].strip() == b"0"
assert contents["compiler.txt"].strip() == b"8.4.3"
binary_digest, binary_path = contents["binary.sha256"].decode().split()
assert len(binary_digest) == 64 and all(c in "0123456789abcdef" for c in binary_digest)
assert binary_path.endswith("/bin/sugarscape-tarray")
results = []
for scenario, initial in [("normal", 500), ("rebirth", 2500)]:
    for repetition in [1, 2]:
        name = f"{scenario}-{repetition}"
        assert contents[name + ".stderr"] == b""
        reader = csv.DictReader(io.StringIO(contents[name + ".csv"].decode()))
        assert reader.fieldnames == ["T", "ObservableAgents", "OccupiedCells"]
        rows = list(reader)
        assert [float(row["T"]) for row in rows] == list(range(1000))
        observed = [int(row["ObservableAgents"]) for row in rows]
        occupied = [int(row["OccupiedCells"]) for row in rows]
        assert all(
            0 <= a <= b <= initial for a, b in zip(observed, occupied, strict=True)
        )
        if scenario == "normal":
            assert observed == occupied
            assert all(a >= b for a, b in zip(observed[:-1], observed[1:], strict=True))
        else:
            assert occupied == [2500] * 1000
            assert any(a < b for a, b in zip(observed, occupied, strict=True))
        results.append(
            {
                "scenario": scenario,
                "repetition": repetition,
                "observations": len(rows),
                "terminal_observables": observed[-1],
                "terminal_occupied": occupied[-1],
                "minimum_observables": min(observed),
                "minimum_occupied": min(occupied),
                "different_count_steps": sum(
                    a != b for a, b in zip(observed, occupied, strict=True)
                ),
                "maximum_count_gap": max(
                    b - a for a, b in zip(observed, occupied, strict=True)
                ),
                "trajectory_sha256": hashlib.sha256(
                    contents[name + ".csv"]
                ).hexdigest(),
            }
        )
report = {
    "archive_sha256": receipt["sha256"],
    "protocol_sha256": hashlib.sha256(contents["protocol.json"]).hexdigest(),
    "compiler": "8.4.3",
    "binary_sha256": binary_digest,
    "runs": results,
    "scope": "Four complete original TArray workflows; observation semantics only. No timing or statistical equivalence claim. Recorded binary digest is provenance, not independent binary reconstruction.",
}
args.output.mkdir(parents=True, exist_ok=False)
(args.output / "audit.json").write_text(json.dumps(report, indent=2) + "\n")
(args.output / "member-sha256.json").write_text(
    json.dumps(
        {name: hashlib.sha256(data).hexdigest() for name, data in contents.items()},
        indent=2,
    )
    + "\n"
)
print(json.dumps(report))
