"""Retain nonfinite native holdings as failed numerical validation, after observer parity."""

import argparse
import csv
import hashlib
import json
import math
from pathlib import Path

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("native", type=Path)
parser.add_argument("observed", type=Path)
parser.add_argument("output", type=Path)
args = parser.parse_args()
assert not args.output.exists()
parity = {}
for name in ["prices.json", "population.csv", "health.csv", "initial-agents.json"]:
    raw = (args.native / name).read_bytes()
    assert raw == (args.observed / name).read_bytes(), name
    parity[name] = hashlib.sha256(raw).hexdigest()
for run in [args.native, args.observed]:
    assert json.loads((run / "exit.json").read_text()) == {"exit_code": 0}
    assert json.loads((run / "complete.json").read_text())["steps"] == 1000
    assert json.loads((run / "manifest.json").read_text())["pythonhashseed"] == "0"
with (args.native / "health.csv").open() as stream:
    health = list(csv.DictReader(stream))
invalid = [
    r
    for r in health
    if any(not math.isfinite(float(r[k])) for k in ["Sugar_Level", "Spice_Level"])
]
report = {
    "numeric_validation": "failed" if invalid else "passed",
    "byte_identical_native_files": parity,
    "health_records": len(health),
    "nonfinite_health_records": len(invalid),
    "first_nonfinite_records": invalid[:10],
    "scope": "Native output parity validates observer neutrality, not numerical correctness. Nonfinite holdings prevent accepting economic outcomes. No paper-level negative verdict.",
}
args.output.mkdir(parents=True, exist_ok=False)
(args.output / "diagnostic.json").write_text(
    json.dumps(report, indent=2, allow_nan=False) + "\n"
)
print(json.dumps(report))
