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
    hashlib.sha256((root / "terminal-recovery-001.tar.gz").read_bytes()).hexdigest()
    == "df1dc09179075d0437eec198fe0b246aaba98e7cdbeeae3af759a04bf9eee976"
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
assert (
    json.loads(
        (root / "terminal-recovery-001/reference-queue-001/plan.json").read_text()
    )
    == plan
)
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
partial_intervals = []
verified = {}
assert (
    json.loads(
        (root / "terminal-recovery-001/reference-queue-terminal.json").read_text()
    )["exit_code"]
    == 124
)
for chunk in sorted(
    (root / "terminal-recovery-001/reference-queue-001").glob("rows-*")
):
    manifest = json.loads((chunk / "manifest.json").read_text())
    assert manifest["reference_sha256"] == reference_hash
    assert manifest["rows"] == 55000 and manifest["steps_each"] == 10000
    start, stop = map(int, manifest["command"][-3:-1])
    assert [start, stop] in plan["ranges"]
    assert chunk.name == f"rows-{start}-{stop}"
    sealed = (chunk / "audit/audit.json").exists()
    if sealed:
        assert json.loads((chunk / "exit.json").read_text())["exit_code"] == 0
    else:
        assert not (chunk / "exit.json").exists()
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
    if sealed:
        assert data == (chunk / "audit/results.csv").read_bytes()
    rows = list(csv.DictReader(data.decode().splitlines()))
    assert 0 < len(rows) <= stop - start
    if sealed:
        assert len(rows) == stop - start
    else:
        partial_intervals.append([start, start + len(rows)])
    for index, row in enumerate(rows, start):
        assert int(row["row"]) == index and index not in seen
        seen[index] = row
    intervals.append([start, start + len(rows)])
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
missing = sorted(set(range(55000)) - set(seen))
remaining = []
for index in missing:
    if (
        remaining
        and remaining[-1][1] == index
        and remaining[-1][1] - remaining[-1][0] < 100
    ):
        remaining[-1][1] += 1
    else:
        remaining.append([index, index + 1])
assert len(verified) == 53
report = {
    "archive_sha256": hashlib.sha256(
        (root / "terminal-recovery-001.tar.gz").read_bytes()
    ).hexdigest(),
    "chunks": len(intervals),
    "interrupted_chunks": len(partial_intervals),
    "validated_interrupted_intervals": partial_intervals,
    "remaining_rows": len(missing),
    "remaining_disjoint_ranges": remaining,
    "intervals": sorted(intervals),
    "remote_rows": len(seen) - len(baseline),
    "baseline_unique_rows": len(baseline),
    "baseline_agreeing_duplicates": baseline_duplicates,
    "cumulative_unique_rows": len(seen),
    "exact_gini_comparisons": len(seen) * 2,
    "source_dependency_files_verified": len(verified),
    "reference_sha256": reference_hash,
    "scope": "Frozen baseline plus sealed chunks and complete rows from terminal interrupted chunks; each index counts once. The full 55,000-row reference and generated-landscape study remain incomplete.",
}
with args.output.open("x") as stream:
    stream.write(json.dumps(report, indent=2) + "\n")
print(json.dumps({k: v for k, v in report.items() if k != "intervals"}))
