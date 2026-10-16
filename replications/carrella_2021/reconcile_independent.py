"""Audit and reconcile disjoint independent runs into original parameter-row order."""

import argparse
import csv
import hashlib
import io
import json
from pathlib import Path
import subprocess
import sys

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("parameters", type=Path)
parser.add_argument("reference", type=Path)
parser.add_argument("mode", choices=["prefix", "complete"])
parser.add_argument("output", type=Path)
parser.add_argument("runs", type=Path, nargs="+")
args = parser.parse_args()
root = Path(__file__).resolve().parent
sources = json.loads((root / "source-audit.json").read_text())["sha256"]
parameter_hash = hashlib.sha256(args.parameters.read_bytes()).hexdigest()
reference_bytes = args.reference.read_bytes()
reference_hash = hashlib.sha256(reference_bytes).hexdigest()
assert parameter_hash == sources["data/sugarscape/params_sugarscape.csv"]
assert reference_hash == sources["data/sugarscape/sugarscape.csv"]
reference = list(csv.DictReader(io.StringIO(reference_bytes.decode())))
assert len(reference) == 5000 and len(reference[0]) == 150
source_hashes = {
    name: hashlib.sha256((root / name).read_bytes()).hexdigest()
    for name in ["model.py", "run_independent.py", "INDEPENDENT_ENSEMBLE.md"]
}
manifests = [json.loads((run / "manifest.json").read_text()) for run in args.runs]
runtime = {key: manifests[0][key] for key in ["python", "numpy", "pydantic"]}
for manifest in manifests:
    assert manifest["source_sha256"] == source_hashes
    assert (
        manifest["parameter_sha256"] == parameter_hash
        and manifest["reference_sha256"] == reference_hash
    )
    assert {key: manifest[key] for key in runtime} == runtime
args.output.mkdir(parents=True, exist_ok=False)
merged = {}
provenance = []
for number, run in enumerate(args.runs):
    audit_dir = args.output / f"audit-{number}"
    subprocess.run(
        [
            sys.executable,
            str(root / "audit_independent.py"),
            str(args.parameters),
            str(run),
            "prefix",
            str(audit_dir),
        ],
        check=True,
    )
    audit = json.loads((audit_dir / "analysis.json").read_text())
    records = [
        json.loads(line)
        for line in (audit_dir / "ledger-snapshot.jsonl").read_text().splitlines()
    ]
    summary_bytes = (audit_dir / "summary-snapshot.csv").read_bytes()
    assert hashlib.sha256(summary_bytes).hexdigest() == audit["summary_sha256"]
    rows = list(csv.DictReader(io.StringIO(summary_bytes.decode())))[: len(records)]
    assert len(rows) == len(records) == audit["validated_inputs"]
    for record, row in zip(records, rows):
        index = record["row"]
        assert index not in merged, (
            f"Duplicate independent input {index}; exclude overlapping runs or validation probes"
        )
        assert row.keys() == reference[0].keys()
        merged[index] = row
    provenance.append(
        {
            "run": str(run.resolve()),
            "audit": audit_dir.name,
            "interval": audit["interval"],
            "manifest_sha256": audit["manifest_sha256"],
            "ledger_sha256": audit["ledger_sha256"],
            "summary_sha256": audit["summary_sha256"],
        }
    )
indices = sorted(merged)
assert set(indices) <= set(range(5000))
missing = sorted(set(range(5000)) - set(indices))
missing_intervals = []
for index in missing:
    if missing_intervals and missing_intervals[-1][1] == index:
        missing_intervals[-1][1] = index + 1
    else:
        missing_intervals.append([index, index + 1])
complete = not missing
name = (
    "summary_statistics.csv"
    if args.mode == "complete"
    else "partial_summary_statistics.csv"
)
report = {
    "mode": args.mode,
    "validated_inputs": len(indices),
    "required_inputs": 5000,
    "statistics_recomputed": 150 * len(indices),
    "complete_original_ensemble": complete,
    "missing_intervals": missing_intervals,
    "summary_file": name,
    "parameter_sha256": parameter_hash,
    "reference_sha256": reference_hash,
    "source_sha256": source_hashes,
    "runtime": runtime,
    "inputs": provenance,
    "scope": "Audited independent-run integrity and original-row ordering. No native-distribution, estimator, or paper-equivalence verdict.",
}
(args.output / "coverage.json").write_text(json.dumps(report, indent=2) + "\n")
assert args.mode == "prefix" or complete, (
    "Incomplete original ensemble; no complete calibration table written"
)
with (args.output / name).open("x", newline="") as stream:
    writer = csv.DictWriter(stream, fieldnames=list(reference[0]))
    writer.writeheader()
    writer.writerows(merged[index] for index in indices)
with (args.output / "row-index.csv").open("x", newline="") as stream:
    writer = csv.writer(stream)
    writer.writerow(["original_row"])
    writer.writerows([index] for index in indices)
report["summary_sha256"] = hashlib.sha256((args.output / name).read_bytes()).hexdigest()
(args.output / "coverage.json").write_text(json.dumps(report, indent=2) + "\n")
print(
    json.dumps(
        {
            key: report[key]
            for key in [
                "mode",
                "validated_inputs",
                "complete_original_ensemble",
                "missing_intervals",
            ]
        }
    )
)
