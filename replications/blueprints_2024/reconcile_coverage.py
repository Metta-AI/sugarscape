"""Reconcile audited original-seed intervals without counting repeat runs twice."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import zipfile

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("archive", type=Path)
parser.add_argument("output", type=Path)
parser.add_argument("audits", nargs="+", type=Path)
args = parser.parse_args()
archive_hash = hashlib.sha256(args.archive.read_bytes()).hexdigest()
assert archive_hash == "319c38c77cdeb9f3bd618ce6c57e14e93c35e2be282c01332d42cff58327f525"
with zipfile.ZipFile(args.archive) as archive:
    configs = [json.loads(archive.read(name)) for name in archive.namelist()]
models = sorted({c["agentDecisionModels"][0] for c in configs})
assert len(models) == 4 and len(configs) == 2000
schedules = {m: sorted(c["seed"] for c in configs if c["agentDecisionModels"] == [m]) for m in models}
assert all(len(s) == len(set(s)) == 500 for s in schedules.values())
assert all(s == schedules[models[0]] for s in schedules.values())
covered = {m: {} for m in models}
inputs = []
duplicates = 0
for path in args.audits:
    raw = path.read_bytes()
    audit = json.loads(raw)
    model, start, stop = audit["model"], audit["start"], audit["stop"]
    assert 0 <= start < stop <= 500
    assert audit["runs"] == stop - start == len(audit["results"])
    assert [r["seed"] for r in audit["results"]] == schedules[model][start:stop]
    assert sum(r["observations"] for r in audit["results"]) == audit["observations"]
    counts = Counter({"dead": 0, "worse": 0, "better_or_equal": 0})
    for index, row in enumerate(audit["results"], start):
        assert 0 < row["observations"] <= 5001
        population = row["final_population"]
        outcome = "dead" if population == 0 else "worse" if population < 250 else "better_or_equal"
        assert row["outcome"] == outcome
        counts[outcome] += 1
        if index in covered[model]:
            assert covered[model][index] == row, (model, index, "Conflicting repeated seed")
            duplicates += 1
        else:
            covered[model][index] = row
    assert dict(counts) == audit["counts"]
    inputs.append({"path": str(path), "sha256": hashlib.sha256(raw).hexdigest(), "model": model, "interval": [start, stop]})
coverage = []
for model in models:
    rows = covered[model]
    intervals = []
    for index in sorted(rows):
        if intervals and intervals[-1][1] == index:
            intervals[-1][1] += 1
        else:
            intervals.append([index, index + 1])
    missing = [index for index in range(500) if index not in rows]
    prefix_end = missing[0] if missing else 500
    coverage.append({"model": model, "validated_interval": [0, prefix_end],
                     "validated_intervals": intervals, "validated_runs": len(rows), "missing_indices": missing,
                     "required_runs": 500,
                     "observations": sum(r["observations"] for r in rows.values()),
                     "partial_counts": dict(Counter(r["outcome"] for r in rows.values())),
                     "next_seed": [schedules[model][index] for index in missing[:1]]})
report = {"archive_sha256": archive_hash, "inputs": inputs, "models": coverage,
          "unique_runs": sum(len(rows) for rows in covered.values()), "excluded_duplicate_records": duplicates,
          "complete_homogeneous_grid": all(len(rows) == 500 for rows in covered.values()),
          "scope": "Union of independently audited intervals. Partial outcome counts are not full-paper estimates. Failed, unledgered runs are excluded."}
args.output.mkdir(parents=True, exist_ok=False)
(args.output / "coverage.json").write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps({k: v for k, v in report.items() if k != "inputs"}))
