"""Compare complete fixed-seed spice audits without inventing equivalence bounds."""

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
reports = [json.loads(path.read_text()) for path in [args.original, args.corrected]]
for report in reports:
    assert report["complete_ensemble"] and report["validated_pairs"] == 100
    assert [row["index"] for row in report["results"]] == list(range(100))
assert reports[1]["source_variant"] == "corrected"
assert [r["seed"] for r in reports[0]["results"]] == [
    r["seed"] for r in reports[1]["results"]
]
comparisons = []
for key in ["spice_book", "trade_off"]:
    for metric in ["at100", "at500", "at1000", "late801_1000"]:
        values = np.array(
            [
                [
                    r["scenarios"][key]["population_metrics"][metric]
                    for r in report["results"]
                ]
                for report in reports
            ]
        )
        assert values.shape == (2, 100) and np.isfinite(values).all()
        delta = values[1] - values[0]
        mean = float(delta.mean())
        margin = float(stats.t.ppf(0.975, 99) * stats.sem(delta))
        comparisons.append(
            {
                "scenario": key,
                "metric": metric,
                "n": 100,
                "corrected_minus_original": {
                    "mean": mean,
                    "ci95": [mean - margin, mean + margin],
                },
            }
        )
report = {
    "input_sha256": {
        label: hashlib.sha256(path.read_bytes()).hexdigest()
        for label, path in zip(
            ["original", "corrected"], [args.original, args.corrected], strict=True
        )
    },
    "comparisons": comparisons,
    "scope": (
        "Same-seed source sensitivity; pointwise 95% intervals, not simultaneous intervals. "
        "No full-paper or approximate-target equivalence verdict."
    ),
}
with args.output.open("x") as stream:
    stream.write(json.dumps(report, indent=2, allow_nan=False) + "\n")
print(json.dumps(comparisons))
