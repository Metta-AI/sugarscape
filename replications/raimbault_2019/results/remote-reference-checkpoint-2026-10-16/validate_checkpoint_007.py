import argparse
import csv
import hashlib
import json
from pathlib import Path

parser = argparse.ArgumentParser(
    description="Validate the complete retained reference checkpoint against pinned native inputs."
)
parser.add_argument("evidence_root", type=Path)
parser.add_argument("output", type=Path)
args = parser.parse_args()
root = args.evidence_root.resolve()
assert (
    hashlib.sha256((root / "reference-checkpoint-007.tar.gz").read_bytes()).hexdigest()
    == "ec2b3af14f0cb9fdc9cc1e945fbe08e3a5368b4bdfd0e8e155adfd81ad839806"
)
runtime = root.parent / "remote-cpu-pilot-001/local-package-proof-002"
reference_bytes = (runtime / "reference.csv").read_bytes()
reference_hash = hashlib.sha256(reference_bytes).hexdigest()
assert (
    reference_hash == "2fc276934c6c50994a2c24196b7da4231383ef3d13f86804b5c38cb0d1d93add"
)
reference = list(csv.DictReader(reference_bytes.decode().splitlines()))
assert len(reference) == 55000
plan = json.loads((root / "production-plan.json").read_text())
assert json.loads((root / "checkpoint-007/plan.json").read_text()) == plan
seen = {}
baseline_duplicates = 0
for file in sorted((root / "checkpoint").rglob("results.csv")):
    for row in csv.DictReader(file.open()):
        index = int(row["row"])
        if index in seen:
            assert seen[index] == row
            baseline_duplicates += 1
        seen[index] = row
assert len(seen) == 7933
baseline = set(seen)
intervals = []
verified = {}
for chunk in sorted((root / "checkpoint-007").glob("rows-*")):
    manifest = json.loads((chunk / "manifest.json").read_text())
    assert manifest["reference_sha256"] == reference_hash
    assert manifest["rows"] == 55000 and manifest["steps_each"] == 10000
    start, stop = map(int, manifest["command"][-3:-1])
    assert [start, stop] in plan["ranges"]
    assert chunk.name == f"rows-{start}-{stop}"
    assert json.loads((chunk / "exit.json").read_text())["exit_code"] == 0
    for kind in ["source_sha256", "dependencies_sha256"]:
        for name, checksum in manifest[kind].items():
            relative = Path(name).relative_to("/root/sugarscape/proof-002")
            if name not in verified:
                verified[name] = hashlib.sha256(
                    (runtime / relative).read_bytes()
                ).hexdigest()
            assert verified[name] == checksum
    data = (chunk / "results.csv").read_bytes()
    assert data.endswith(b"\n")
    assert data == (chunk / "audit/results.csv").read_bytes()
    rows = list(csv.DictReader(data.decode().splitlines()))
    assert len(rows) == stop - start
    for index, row in enumerate(rows, start):
        assert int(row["row"]) == index and index not in seen
        seen[index] = row
    intervals.append([start, stop])
for index, row in seen.items():
    archived = reference[index]
    assert int(row["seed"]) == int(archived["replication"])
    assert float(row["population"]) == float(archived["population"])
    assert float(row["ticks"]) == 10000
    for metric in ["gini", "mwgini"]:
        assert 0 <= float(row[metric]) <= 1
        assert (
            float(row[metric])
            == float(archived[metric])
            == float(row["archived_" + metric])
        )
report = {
    "archive_sha256": hashlib.sha256(
        (root / "reference-checkpoint-007.tar.gz").read_bytes()
    ).hexdigest(),
    "chunks": len(intervals),
    "intervals": sorted(intervals),
    "remote_rows": len(seen) - len(baseline),
    "baseline_unique_rows": len(baseline),
    "baseline_agreeing_duplicates": baseline_duplicates,
    "cumulative_unique_rows": len(seen),
    "exact_gini_comparisons": len(seen) * 2,
    "source_dependency_files_verified": len(verified),
    "reference_sha256": reference_hash,
    "scope": "Frozen baseline plus sealed remote chunks; earlier remote checkpoints are contained here and are not added again. The full 55,000-row reference and generated-landscape study remain incomplete.",
}
with args.output.open("x") as stream:
    stream.write(json.dumps(report, indent=2) + "\n")
print(json.dumps({k: v for k, v in report.items() if k != "intervals"}))
