"""Validate a disjoint terminal continuation against the original 55,000 inputs."""

import argparse
import csv
import hashlib
import json
from pathlib import Path

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("run", type=Path)
parser.add_argument("runtime", type=Path)
parser.add_argument("output", type=Path)
parser.add_argument(
    "--prior-audit",
    type=Path,
    default=Path(__file__).resolve().parent
    / "results/terminal-reference-2026-10-17/audit.json",
    help="Previously validated union audit defining the disjoint remaining inputs",
)
args = parser.parse_args()
prior = json.loads(args.prior_audit.read_text())
baseline = prior["cumulative_unique_rows"]
assert 0 <= baseline < 55000
prior_ranges = prior["remaining_disjoint_ranges"]
assert all(0 <= start < stop <= 55000 for start, stop in prior_ranges)
assert all(left[1] <= right[0] for left, right in zip(prior_ranges, prior_ranges[1:]))
remaining = {
    i for start, stop in prior["remaining_disjoint_ranges"] for i in range(start, stop)
}
assert len(remaining) == 55000 - baseline
reference_bytes = (args.runtime / "reference.csv").read_bytes()
reference_hash = hashlib.sha256(reference_bytes).hexdigest()
assert (
    reference_hash == "2fc276934c6c50994a2c24196b7da4231383ef3d13f86804b5c38cb0d1d93add"
)
reference = list(csv.DictReader(reference_bytes.decode().splitlines()))
assert len(reference) == 55000
plan = json.loads((args.run / "production-plan.json").read_text())
assert plan == json.loads((args.run / "results/plan.json").read_text())
assert plan["ranges"] == prior["remaining_disjoint_ranges"]
terminal = json.loads((args.run / "terminal.json").read_text())
assert terminal in ({"exit_code": 0}, {"exit_code": 124})
seen = set()
verified = {}
intervals = []
partial = []
for chunk in sorted((args.run / "results").glob("rows-*")):
    manifest = json.loads((chunk / "manifest.json").read_text())
    assert manifest["reference_sha256"] == reference_hash
    assert manifest["rows"] == 55000 and manifest["steps_each"] == 10000
    start, stop = map(int, manifest["command"][-3:-1])
    assert [start, stop] in plan["ranges"]
    assert chunk.name == f"rows-{start}-{stop}"
    for kind in ("source_sha256", "dependencies_sha256"):
        for name, digest in manifest[kind].items():
            relative = Path(name).relative_to("/root/sugarscape/proof-002")
            if name not in verified:
                verified[name] = hashlib.sha256(
                    (args.runtime / relative).read_bytes()
                ).hexdigest()
            assert verified[name] == digest
    raw = (chunk / "results.csv").read_bytes()
    assert raw.endswith(b"\n")
    rows = list(csv.DictReader(raw.decode().splitlines()))
    assert 0 <= len(rows) <= stop - start
    sealed = (chunk / "audit/audit.json").exists()
    if sealed:
        assert json.loads((chunk / "exit.json").read_text())["exit_code"] == 0
        assert len(rows) == stop - start
        assert raw == (chunk / "audit/results.csv").read_bytes()
    else:
        assert terminal["exit_code"] == 124
        assert not (chunk / "exit.json").exists()
        partial.append([start, start + len(rows)])
    for index, row in enumerate(rows, start):
        assert int(row["row"]) == index and index in remaining and index not in seen
        seen.add(index)
        archived = reference[index]
        assert int(row["seed"]) == int(archived["replication"])
        assert float(row["population"]) == float(archived["population"])
        assert float(row["ticks"]) == 10000
        for metric in ("gini", "mwgini"):
            value = float(row[metric])
            assert 0 <= value <= 1
            assert value == float(archived[metric]) == float(row["archived_" + metric])
    intervals.append([start, start + len(rows)])
assert len(verified) == 53
missing = sorted(remaining - seen)
if terminal["exit_code"] == 0:
    assert not missing and not partial
ranges = []
for index in missing:
    if ranges and ranges[-1][1] == index and ranges[-1][1] - ranges[-1][0] < 100:
        ranges[-1][1] += 1
    else:
        ranges.append([index, index + 1])
report = {
    "baseline_unique_rows": baseline,
    "new_unique_rows": len(seen),
    "cumulative_unique_rows": baseline + len(seen),
    "exact_gini_comparisons": 2 * (baseline + len(seen)),
    "remaining_rows": len(missing),
    "remaining_disjoint_ranges": ranges,
    "intervals": intervals,
    "interrupted_intervals": partial,
    "source_dependency_files_verified": len(verified),
    "reference_sha256": reference_hash,
    "scope": (
        "Complete native rows from terminal chunks only; disjoint from the previously re-audited baseline. Interrupted simulations receive no credit. Full reference and generated ensembles remain required."
        if missing
        else "All 55,000 reference inputs are validated across disjoint audited batches. Generated-landscape and spatial-sensitivity requirements remain outstanding."
    ),
}
with args.output.open("x") as stream:
    stream.write(json.dumps(report, indent=2) + "\n")
print(
    json.dumps(
        {
            key: value
            for key, value in report.items()
            if key not in ("intervals", "remaining_disjoint_ranges")
        }
    )
)
