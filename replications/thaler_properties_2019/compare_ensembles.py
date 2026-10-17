"""Compare complete, defined paired ensembles without replacing historical results."""

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
from scipy import stats

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("original", type=Path)
parser.add_argument("corrected", type=Path)
parser.add_argument("output", type=Path)
args = parser.parse_args()
original = json.loads(args.original.read_text())
corrected = json.loads(args.corrected.read_text())
assert original["scenario"] == corrected["scenario"]
for report in [original, corrected]:
    assert report["complete_ensemble"] and report["validated_runs"] == 100
    assert [r["index"] for r in report["results"]] == list(range(100))
    assert all(r["status"] == "defined" for r in report["results"]), (
        "Undefined statistics cannot be silently dropped"
    )
assert [r["seed"] for r in original["results"]] == [
    r["seed"] for r in corrected["results"]
]
metrics = list(original["results"][0]["statistics"])
assert all(
    list(r["statistics"]) == metrics
    for report in [original, corrected]
    for r in report["results"]
)
rows = []
for metric in metrics:
    before = np.array([r["statistics"][metric] for r in original["results"]])
    after = np.array([r["statistics"][metric] for r in corrected["results"]])
    assert np.isfinite(before).all() and np.isfinite(after).all()
    differences = after - before
    mean = float(differences.mean())
    margin = float(stats.t.ppf(0.975, 99) * stats.sem(differences))
    rows.append(
        {
            "metric": metric,
            "n": 100,
            "original_mean": float(before.mean()),
            "corrected_mean": float(after.mean()),
            "paired_mean_change": mean,
            "paired_ci95": [mean - margin, mean + margin],
            "per_seed_changes": differences.tolist(),
        }
    )
report = {
    "scenario": original["scenario"],
    "seeds": [r["seed"] for r in original["results"]],
    "original_audit_sha256": hashlib.sha256(args.original.read_bytes()).hexdigest(),
    "corrected_audit_sha256": hashlib.sha256(args.corrected.read_bytes()).hexdigest(),
    "comparisons": rows,
    "scope": "Exploratory paired source-correction effects. Same 100 seeds, all defined outcomes. No historical results replaced and no full-paper verdict.",
}
with args.output.open("x") as stream:
    stream.write(json.dumps(report, indent=2, allow_nan=False) + "\n")
print(
    json.dumps(
        {
            "scenario": report["scenario"],
            "comparisons": [
                {k: v for k, v in r.items() if k != "per_seed_changes"} for r in rows
            ],
        }
    )
)
