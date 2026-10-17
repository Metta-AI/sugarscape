"""Describe price movement toward one using complete audited paper ensembles."""

import argparse
import csv
import hashlib
import itertools
import json
import math
from pathlib import Path
import statistics

from scipy.stats import t


def interval(values):
    mean = statistics.fmean(values)
    radius = (
        float(t.ppf(0.975, len(values) - 1))
        * statistics.stdev(values)
        / math.sqrt(len(values))
    )
    return {"n": len(values), "mean": mean, "low": mean - radius, "high": mean + radius}


parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("phase1", type=Path)
parser.add_argument("phase2", type=Path)
parser.add_argument("phase3", type=Path)
parser.add_argument("output", type=Path)
args = parser.parse_args()
inputs = {}
values = {}
metrics = ["abs_log_geometric_mean", "sample_sd_log_price"]
step_records = 0
for phase, directory, required in [
    (1, args.phase1, 300),
    (2, args.phase2, 600),
    (3, args.phase3, 1200),
]:
    report_path = directory / "reconciliation.json"
    raw = report_path.read_bytes()
    report = json.loads(raw)
    assert report["phase"] == phase and report["complete_grid"]
    assert report["validated_runs"] == report["required_runs"] == required
    assert report["missing_ordinals"] == []
    inputs[str(report_path)] = hashlib.sha256(raw).hexdigest()
    phase_keys = set()
    for index, segment in enumerate(report["segments"]):
        source = directory / f"segment-{index:02d}"
        assert (
            hashlib.sha256((source / "audit.json").read_bytes()).hexdigest()
            == segment["audit_sha256"]
        )
        path = source / "price-measurements.csv"
        inputs[str(path)] = hashlib.sha256(path.read_bytes()).hexdigest()
        with path.open() as stream:
            for row in csv.DictReader(stream):
                if phase == 1:
                    condition = f"phase1-{row['variant']}"
                else:
                    selector = row["selector"] if phase == 3 else "none"
                    condition = f"{row['approach']}-{row['threshold']}-{selector}"
                key = (condition, int(row["numpy_seed"]))
                if key not in values:
                    values[key] = {
                        "steps": set(),
                        "windows": {
                            window: {metric: [] for metric in metrics}
                            for window in ["early", "late"]
                        },
                    }
                phase_keys.add(key)
                run = values[key]
                step, trades = int(row["step"]), int(row["trades"])
                assert step not in run["steps"] and 1 <= step <= 1000
                run["steps"].add(step)
                assert (row["geometric_mean_price"] != "") == (trades > 0)
                assert (row["sample_sd_log_price"] != "") == (trades >= 2)
                if step <= 100 or step >= 901:
                    window = run["windows"]["early" if step <= 100 else "late"]
                    if trades:
                        price = float(row["geometric_mean_price"])
                        assert price > 0 and math.isfinite(price)
                        window["abs_log_geometric_mean"].append(abs(math.log(price)))
                    if trades >= 2:
                        dispersion = float(row["sample_sd_log_price"])
                        assert dispersion >= 0 and math.isfinite(dispersion)
                        window["sample_sd_log_price"].append(dispersion)
                step_records += 1
    assert len(phase_keys) == required
assert len(values) == 2100 and step_records == 2100000
conditions = sorted({condition for condition, _ in values})
assert set(values) == set(itertools.product(conditions, range(100)))
rows = []
means = {}
for (condition, seed), run in sorted(values.items()):
    assert run["steps"] == set(range(1, 1001))
    for window, measurements in run["windows"].items():
        for metric, observed in measurements.items():
            mean = statistics.fmean(observed) if observed else None
            means[condition, seed, window, metric] = mean
            rows.append(
                {
                    "condition": condition,
                    "seed": seed,
                    "window": window,
                    "metric": metric,
                    "defined_steps": len(observed),
                    "mean": mean,
                }
            )
estimates = []
changes = []
contrasts = []
for condition in conditions:
    for metric in metrics:
        for window in ["early", "late"]:
            observed = [
                means[condition, seed, window, metric]
                for seed in range(100)
                if means[condition, seed, window, metric] is not None
            ]
            estimates.append(
                {
                    "condition": condition,
                    "window": window,
                    "metric": metric,
                    **interval(observed),
                }
            )
        paired = [
            means[condition, seed, "late", metric]
            - means[condition, seed, "early", metric]
            for seed in range(100)
            if means[condition, seed, "late", metric] is not None
            and means[condition, seed, "early", metric] is not None
        ]
        changes.append({"condition": condition, "metric": metric, **interval(paired)})
for approach, threshold, selector, metric in itertools.product(
    ["explicit", "network"], [1, 5, 10], ["released", "corrected-highest"], metrics
):
    left, right = f"{approach}-{threshold}-{selector}", f"{approach}-{threshold}-none"
    paired = [
        means[left, seed, "late", metric] - means[right, seed, "late", metric]
        for seed in range(100)
        if means[left, seed, "late", metric] is not None
        and means[right, seed, "late", metric] is not None
    ]
    contrasts.append(
        {"left": left, "right": right, "metric": metric, **interval(paired)}
    )
args.output.mkdir(parents=True, exist_ok=False)
with (args.output / "run-measurements.csv").open("x") as stream:
    writer = csv.DictWriter(stream, fieldnames=list(rows[0]), lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
result = {
    "input_sha256": inputs,
    "runs": len(values),
    "step_records": step_records,
    "estimates": estimates,
    "paired_late_minus_early": changes,
    "paired_late_policy_minus_none": contrasts,
    "scope": "Retrospective descriptive windows1-100 and901-1000; abs(log(geometric mean price)) measures distance from price1. SD(log(price)) matches native histogram. Equal weighting of defined timesteps within each run, then independent seeds as inference units; missing statistics remain missing, comparisons use jointly defined pairs. Pointwise Student-t95% CIs, no multiplicity adjustment/equivalence margin. These finite-window contrasts cannot prove asymptotic convergence or nonconvergence; they quantify paper directions at1000steps. Corrected-highest is sensitivity only.",
}
(args.output / "analysis.json").write_text(
    json.dumps(result, indent=2, allow_nan=False) + "\n"
)
print(
    json.dumps(
        {
            "runs": len(values),
            "step_records": step_records,
            "intervals": len(estimates) + len(changes) + len(contrasts),
        }
    )
)
