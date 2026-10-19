"""Prepare isolated author estimators from a complete audited independent ensemble."""

import argparse
import csv
import hashlib
import io
import json
import math
from pathlib import Path

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("author_source", type=Path)
parser.add_argument("reconciliation", type=Path)
parser.add_argument("output", type=Path)
args = parser.parse_args()
root = Path(__file__).resolve().parent
pins = json.loads((root / "source-audit.json").read_text())["sha256"]
coverage_bytes = (args.reconciliation / "coverage.json").read_bytes()
coverage = json.loads(coverage_bytes)
assert coverage["mode"] == "complete" and coverage["complete_original_ensemble"]
assert coverage["validated_inputs"] == coverage["required_inputs"] == 5000
assert coverage["missing_intervals"] == []
assert coverage["summary_file"] == "summary_statistics.csv"
assert coverage["parameter_sha256"] == pins["data/sugarscape/params_sugarscape.csv"]
assert coverage["reference_sha256"] == pins["data/sugarscape/sugarscape.csv"]
for name, expected in coverage["source_sha256"].items():
    assert hashlib.sha256((root / name).read_bytes()).hexdigest() == expected, name
with (args.reconciliation / "row-index.csv").open(newline="") as stream:
    assert [int(row["original_row"]) for row in csv.DictReader(stream)] == list(
        range(5000)
    )
summary = (args.reconciliation / "summary_statistics.csv").read_bytes()
assert hashlib.sha256(summary).hexdigest() == coverage["summary_sha256"]
rows = list(csv.DictReader(io.StringIO(summary.decode())))
assert len(rows) == 5000 and len(rows[0]) == 150
assert all(math.isfinite(float(value)) for row in rows for value in row.values())
files = {}
for name in ["setup.R", "data/sugarscape/params_sugarscape.csv"]:
    files[name] = (args.author_source / name).read_bytes()
    assert hashlib.sha256(files[name]).hexdigest() == pins[name], name
files["data/sugarscape/sugarscape.csv"] = summary
args.output.mkdir(parents=True, exist_ok=False)
for name, content in files.items():
    destination = args.output / name
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(content)
(args.output / "provenance.json").write_text(
    json.dumps(
        {
            "kind": "independent_simulation_estimator_inputs",
            "reconciliation": str(args.reconciliation.resolve()),
            "coverage_sha256": hashlib.sha256(coverage_bytes).hexdigest(),
            "files_sha256": {
                name: hashlib.sha256(content).hexdigest()
                for name, content in files.items()
            },
            "rows": 5000,
            "scope": "Original author estimator functions and parameter inputs, with audited independent simulation statistics. No estimator result or equivalence claim.",
        },
        indent=2,
    )
    + "\n"
)
print(args.output.resolve())
