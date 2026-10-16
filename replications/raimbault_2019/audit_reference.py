"""Independently verify fixed-landscape replay rows against the original archive."""
import argparse
import csv
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
args = parser.parse_args()
reference_bytes = args.reference.read_bytes()
reference_hash = hashlib.sha256(reference_bytes).hexdigest()
assert reference_hash == "2fc276934c6c50994a2c24196b7da4231383ef3d13f86804b5c38cb0d1d93add"
reference = list(csv.DictReader(io.StringIO(reference_bytes.decode())))
assert len(reference) == 55000
manifest = json.loads((args.run / "manifest.json").read_text())
assert manifest["reference_sha256"] == reference_hash
assert manifest["rows"] == 55000 and manifest["steps_each"] == 10000
for name, checksum in manifest["source_sha256"].items():
    assert hashlib.sha256(Path(name).read_bytes()).hexdigest() == checksum
snapshot = (args.run / "results.csv").read_bytes()
assert snapshot.endswith(b"\n"), "Snapshot caught an incomplete row; retry after the writer flushes"
rows = list(csv.DictReader(io.StringIO(snapshot.decode())))
assert 0 < len(rows) <= 55000
if args.mode == "complete":
    assert json.loads((args.run / "exit.json").read_text())["exit_code"] == 0
    assert len(rows) == 55000
mismatches = []
maximum_errors = {"gini": 0.0, "mwgini": 0.0}
for index, row in enumerate(rows):
    archived = reference[index]
    assert int(row["row"]) == index
    assert int(row["seed"]) == int(archived["replication"])
    assert float(row["population"]) == float(archived["population"])
    assert float(row["ticks"]) == 10000
    for metric in maximum_errors:
        actual = float(row[metric])
        expected = float(archived[metric])
        assert math.isfinite(actual) and 0 <= actual <= 1
        assert float(row["archived_" + metric]) == expected
        error = abs(actual - expected)
        maximum_errors[metric] = max(maximum_errors[metric], error)
        if actual != expected:
            mismatches.append({"row": index, "metric": metric, "actual": actual, "expected": expected, "absolute_error": error})
report = {"mode": args.mode, "rows": len(rows), "required_rows": 55000, "compared_measurements": 2 * len(rows),
          "mismatch_count": len(mismatches), "first_mismatches": mismatches[:20], "maximum_absolute_errors": maximum_errors,
          "reference_sha256": reference_hash, "snapshot_sha256": hashlib.sha256(snapshot).hexdigest(),
          "scope": "Exact native Gini replay for the recorded prefix or complete fixed reference. Generated landscapes and fresh spatial-sensitivity conclusions remain separate."}
args.output.mkdir(parents=True, exist_ok=False)
(args.output / "results.csv").write_bytes(snapshot)
(args.output / "audit.json").write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps(report))
assert not mismatches, "Archived measurement mismatch; inspect the preserved snapshot"
