"""Require grid, registry, and counter agreement through every complete showcase."""
import argparse
import csv
import hashlib
import json
from pathlib import Path
import subprocess

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("batch", type=Path)
parser.add_argument("output", type=Path)
args = parser.parse_args()
manifest = json.loads((args.batch / "manifest.json").read_text())
completed = [json.loads(line) for line in (args.batch / "completed.jsonl").read_text().splitlines()]
assert len(completed) == 34 and all(r["exit_code"] == 0 for r in completed)
engine = Path(manifest["engine"])
for name, checksum in manifest["source_sha256"].items():
    assert hashlib.sha256((engine / name).read_bytes()).hexdigest() == checksum
root = Path(__file__).resolve().parent
args.output.mkdir(parents=True, exist_ok=False)
output = args.output.resolve()
records = []
for target in manifest["targets"]:
    name = target["id"]
    original_command = next(r["command"] for r in completed if r["target"] == name)
    command = [*original_command]
    command[4] = str(root / "AuditReplay.java")
    command.append(str(output / f"{name}-state.csv"))
    with (output / f"{name}-native.csv").open("x") as stdout, (output / f"{name}.stderr").open("x") as stderr:
        subprocess.run(command, cwd=engine, stdout=stdout, stderr=stderr, check=True)
    native = (output / f"{name}-native.csv").read_bytes()
    assert native == (args.batch / f"{name}-repeat1.csv").read_bytes(), "Observation changed native output"
    with (output / f"{name}-state.csv").open() as stream:
        rows = list(csv.DictReader(stream))
    assert [float(r["time"]) for r in rows] == list(range(1002))
    mismatches = [r for r in rows if len({r[k] for k in ["reported_population", "grid_alive", "registered", "registered_alive"]}) != 1]
    record = {"target": name, "observations": len(rows), "native_byte_identical": True,
              "mismatch_observations": len(mismatches), "first_mismatches": mismatches[:3],
              "final": rows[-1], "command": command,
              "state_sha256": hashlib.sha256((output / f"{name}-state.csv").read_bytes()).hexdigest()}
    records.append(record)
    print(json.dumps(record), flush=True)
report = {"variant": manifest["variant"], "observer_sha256": hashlib.sha256((root / "AuditReplay.java").read_bytes()).hexdigest(),
          "configurations": len(records), "observations": sum(r["observations"] for r in records), "results": records}
(output / "audit.json").write_text(json.dumps(report, indent=2) + "\n")
assert all(r["mismatch_observations"] == 0 for r in records), "Population invariant failed; inspect retained state trajectories"
