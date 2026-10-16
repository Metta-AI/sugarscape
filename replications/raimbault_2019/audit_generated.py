"""Audit fresh generated-landscape intervals against the original raw archive."""

import argparse
import csv
import gzip
import hashlib
import io
import json
import math
from pathlib import Path

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("reference", type=Path)
parser.add_argument("run", type=Path)
parser.add_argument("mode", choices=["prefix", "complete"])
parser.add_argument("output", type=Path)
parser.add_argument("--morphology-absolute-tolerance", type=float, required=True)
args = parser.parse_args()
assert math.isfinite(args.morphology_absolute_tolerance)
assert 0 <= args.morphology_absolute_tolerance <= 1e-12
reference_hash = hashlib.sha256()
with gzip.open(args.reference, "rb") as archive:
    while chunk := archive.read(1024 * 1024):
        reference_hash.update(chunk)
assert (
    reference_hash.hexdigest()
    == "1a2cdf93167571ab2943d488017ace08945e7afd3cd8ac4d1410fb214c79c8f5"
)
manifest = json.loads((args.run / "manifest.json").read_text())
assert manifest["reference_sha256"] == reference_hash.hexdigest()
assert manifest["steps_each"] == 10000
start, stop = manifest["requested_interval"]
assert 0 <= start < stop <= 2727994
assert list(map(int, manifest["command"][-3:-1])) == [start, stop]
for field in ["source_sha256", "dependencies_sha256"]:
    assert manifest[field]
    for name, expected_hash in manifest[field].items():
        assert hashlib.sha256(Path(name).read_bytes()).hexdigest() == expected_hash, (
            name
        )
snapshot = (args.run / "results.csv").read_bytes()
assert snapshot.endswith(b"\n"), (
    "Incomplete output row; retry after the producer flushes"
)
rows = list(csv.DictReader(io.StringIO(snapshot.decode())))
assert 0 < len(rows) <= stop - start
if args.mode == "complete":
    assert json.loads((args.run / "exit.json").read_text())["exit_code"] == 0
    assert len(rows) == stop - start
metrics = [
    "gini",
    "mwgini",
    "moran",
    "distance",
    "entropy",
    "slope",
    "rsquared",
    "moranRessource",
    "distanceRessource",
    "entropyRessource",
    "slopeRessource",
    "rsquaredRessource",
]
args.output.mkdir(parents=True, exist_ok=False)
(args.output / "results.csv").write_bytes(snapshot)
maximum_errors = dict.fromkeys(metrics, 0.0)
exact = mismatches = compared_rows = 0
with (
    gzip.open(args.reference, "rt", newline="") as archive,
    (args.output / "deviations.jsonl").open("x") as deviations,
):
    for index, reference in enumerate(csv.DictReader(archive)):
        if index < start:
            continue
        if index == start + len(rows):
            break
        row = rows[index - start]
        assert int(row["row"]) == index
        assert row["id"] == reference["id"] and row["seed"] == reference["replication"]
        assert float(row["population"]) == float(reference["population"])
        assert reference["setup"] == "1" and float(row["ticks"]) == 10000
        for metric in metrics:
            actual, expected = float(row[metric]), float(reference[metric])
            assert math.isfinite(actual) and math.isfinite(expected)
            error = abs(actual - expected)
            tolerance = (
                0.0
                if metric in ["gini", "mwgini"]
                else args.morphology_absolute_tolerance
            )
            maximum_errors[metric] = max(maximum_errors[metric], error)
            exact += error == 0
            mismatches += error > tolerance
            if error:
                deviations.write(
                    json.dumps(
                        {
                            "row": index,
                            "metric": metric,
                            "actual": actual,
                            "expected": expected,
                            "absolute_error": error,
                            "tolerance": tolerance,
                            "within_tolerance": error <= tolerance,
                        }
                    )
                    + "\n"
                )
        compared_rows += 1
assert compared_rows == len(rows)
report = {
    "mode": args.mode,
    "requested_interval": [start, stop],
    "validated_interval": [start, start + len(rows)],
    "rows": len(rows),
    "measurements": len(rows) * len(metrics),
    "exact_measurements": exact,
    "mismatch_count": mismatches,
    "maximum_absolute_errors": maximum_errors,
    "morphology_absolute_tolerance": args.morphology_absolute_tolerance,
    "reference_sha256": reference_hash.hexdigest(),
    "snapshot_sha256": hashlib.sha256(snapshot).hexdigest(),
    "manifest_sha256": hashlib.sha256(
        (args.run / "manifest.json").read_bytes()
    ).hexdigest(),
    "complete_generated_ensemble": args.mode == "complete"
    and start == 0
    and stop == 2727994,
    "scope": "Fresh generated interval only; fixed reference and fresh spatial contrasts remain separate requirements.",
}
(args.output / "audit.json").write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps(report))
assert mismatches == 0, (
    "Measurement mismatch; inspect preserved deviations and snapshot"
)
