"""Analyze complete audited grouping grids, retaining runs as uncertainty units."""

import argparse
import csv
import hashlib
import itertools
import json
import math
from pathlib import Path
import statistics

import numpy as np
from scipy import stats


def interval(values):
    mean = statistics.fmean(values)
    sd = statistics.stdev(values)
    radius = float(stats.t.ppf(0.975, len(values) - 1)) * sd / math.sqrt(len(values))
    return {
        "n": len(values),
        "mean": mean,
        "sample_sd": sd,
        "low": mean - radius,
        "high": mean + radius,
    }


parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("phase2", type=Path)
parser.add_argument("phase1", type=Path)
parser.add_argument("output", type=Path)
args = parser.parse_args()
reports = []
hashes = {}
for path, phase, count in [(args.phase2, 2, 600), (args.phase1, 1, 300)]:
    raw = (path / "reconciliation.json").read_bytes()
    report = json.loads(raw)
    assert report["phase"] == phase and report["complete_grid"]
    assert report["required_runs"] == report["validated_runs"] == count
    assert report["missing_ordinals"] == []
    assert [r["ordinal"] for r in report["runs"]] == list(range(count))
    hashes[str(path / "reconciliation.json")] = hashlib.sha256(raw).hexdigest()
    reports.append(report)
report, baseline_report = reports
conditions = list(itertools.product(["explicit", "network"], [1, 5, 10]))
values = {}
run_rows = []
for approach, threshold in conditions:
    selected = [
        r
        for r in report["runs"]
        if (r["approach"], r["threshold"]) == (approach, threshold)
    ]
    assert [r["numpy_seed"] for r in selected] == list(range(100))
    label = f"{approach}-{threshold}"
    values[label] = [r["final_individual_agents"] for r in selected]
    run_rows.extend(
        {
            "condition": label,
            "seed": r["numpy_seed"],
            "survivors": r["final_individual_agents"],
        }
        for r in selected
    )
baseline_rows = [r for r in baseline_report["runs"] if r["variant"] == "standard"]
assert [r["numpy_seed"] for r in baseline_rows] == list(range(100))
baseline = [r["final_individual_agents"] for r in baseline_rows]
run_rows.extend(
    {
        "condition": "phase1-standard",
        "seed": r["numpy_seed"],
        "survivors": r["final_individual_agents"],
    }
    for r in baseline_rows
)
survivors = {label: interval(v) for label, v in values.items()}
comparisons = []
for left, right in itertools.combinations(values, 2):
    differences = [a - b for a, b in zip(values[left], values[right], strict=True)]
    comparisons.append({"left": left, "right": right, **interval(differences)})
independent = []
for label, v in values.items():
    a, b = (
        statistics.variance(v) / len(v),
        statistics.variance(baseline) / len(baseline),
    )
    degrees = (a + b) ** 2 / (a * a / (len(v) - 1) + b * b / (len(baseline) - 1))
    difference = statistics.fmean(v) - statistics.fmean(baseline)
    radius = float(stats.t.ppf(0.975, degrees)) * math.sqrt(a + b)
    independent.append(
        {
            "condition": label,
            "mean_difference": difference,
            "low": difference - radius,
            "high": difference + radius,
            "welch_degrees_of_freedom": degrees,
        }
    )
measurements = {label: [] for label in values}
for index, segment in enumerate(report["segments"]):
    directory = args.phase2 / f"segment-{index:02d}"
    assert (
        hashlib.sha256((directory / "audit.json").read_bytes()).hexdigest()
        == segment["audit_sha256"]
    )
    path = directory / "price-measurements.csv"
    hashes[str(path)] = hashlib.sha256(path.read_bytes()).hexdigest()
    with path.open() as stream:
        for row in csv.DictReader(stream):
            measurements[f"{row['approach']}-{row['threshold']}"].append(row)
prices = {}
histograms = []
for label, rows in measurements.items():
    assert len(rows) == 100000
    assert {(int(r["numpy_seed"]), int(r["step"])) for r in rows} == set(
        itertools.product(range(100), range(1, 1001))
    )
    assert all(
        (r["geometric_mean_price"] != "") == (int(r["trades"]) > 0) for r in rows
    )
    assert all(
        (r["sample_sd_log_price"] != "") == (int(r["trades"]) >= 2) for r in rows
    )
    dispersion = [
        float(r["sample_sd_log_price"]) for r in rows if r["sample_sd_log_price"] != ""
    ]
    counts, edges = np.histogram(dispersion, bins=500)
    assert sum(counts) == len(dispersion)
    histograms.extend(
        {
            "condition": label,
            "left": float(edges[i]),
            "right": float(edges[i + 1]),
            "count": int(n),
        }
        for i, n in enumerate(counts)
    )
    runs = [[r for r in rows if int(r["numpy_seed"]) == seed] for seed in range(100)]
    windows = {}
    for name, first, last in [("early", 1, 100), ("late", 901, 1000)]:
        selected = [[r for r in run if first <= int(r["step"]) <= last] for run in runs]
        windows[name] = {
            "trades_per_run": interval(
                [sum(int(r["trades"]) for r in run) for run in selected]
            )
        }
        for metric in ["geometric_mean_price", "sample_sd_log_price"]:
            defined = [
                [float(r[metric]) for r in run if r[metric] != ""] for run in selected
            ]
            means = [statistics.fmean(v) for v in defined if v]
            windows[name][metric] = {
                "defined_runs": len(means),
                "defined_steps": sum(map(len, defined)),
                "run_mean_interval": interval(means) if len(means) >= 2 else None,
            }
    prices[label] = {
        "steps": len(rows),
        "no_trade_steps": sum(int(r["trades"]) == 0 for r in rows),
        "undefined_dispersion_steps": len(rows) - len(dispersion),
        "pooled_dispersion_quantiles": np.quantile(
            dispersion, [0, 0.25, 0.5, 0.75, 1]
        ).tolist(),
        "windows": windows,
    }
result = {
    "input_sha256": hashes,
    "survivors": survivors,
    "paired_differences": comparisons,
    "phase1_standard": interval(baseline),
    "independent_baseline_differences": independent,
    "prices": prices,
    "scope": "100 runs per condition. Pointwise Student-t 95% intervals; 15 paired contrasts are not simultaneous intervals. PhaseI standard comparison uses independent Welch intervals as declared. Undefined transaction statistics remain missing; defined-run intervals are conditional. Pooled histograms are descriptive, not independent samples. No equivalence margin, original seeds, or verified paper source pin; no paper-level verdict.",
}
args.output.mkdir(parents=True, exist_ok=False)
(args.output / "analysis.json").write_text(
    json.dumps(result, indent=2, allow_nan=False) + "\n"
)
for filename, rows in [
    ("survivors.csv", run_rows),
    ("dispersion-histograms.csv", histograms),
]:
    with (args.output / filename).open("x") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
print(json.dumps(survivors))
