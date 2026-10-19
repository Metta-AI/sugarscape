"""Audit complete fixed-data SABC1D seed ensembles and summarize observed score ranges."""

import argparse
import csv
import hashlib
import json
import math
from pathlib import Path
import statistics

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("ensemble", type=Path)
parser.add_argument("output", type=Path)
args = parser.parse_args()
root = args.ensemble
repo = Path(__file__).resolve().parent
protocol = json.loads((root / "protocol.json").read_text())
terminal = json.loads((root / "terminal.json").read_text())
assert terminal == {"completed_seeds": protocol["seeds"], "exit_code": 0}
assert protocol["method"] == "sabc_1d" and protocol["cv_seed"] == 0
assert protocol["seeds"] == list(range(1, 11))
size = protocol["size"]
assert size in (1250, 5000)
assert not args.output.exists()
for name, digest in protocol["hashes"].items():
    assert hashlib.sha256(Path(name).read_bytes()).hexdigest() == digest
primary_dir = repo / f"results/sabc1d-{size}-2026-10-15"
with (primary_dir / "metrics.csv").open() as stream:
    primary = {r["parameter"]: float(r["performance"]) for r in csv.DictReader(stream)}
with (primary_dir / "packages.csv").open() as stream:
    primary_packages = {r["Package"]: r["Version"] for r in csv.DictReader(stream)}
relevant = ("abc", "abctools", "R.utils", "dplyr", "purrr", "tidyr", "readr")
published = json.loads((repo / "published_table8.json").read_text())
column = published["columns"].index("Semi-automatic ABC 1D")
targets = {
    r[1]: float(r[column])
    for r in published["rows"]
    if r[0] == f"Sugarscape ABM {size:,}"
}
assert targets.keys() == primary.keys() and len(targets) == 5
scores = []
checks = []
reference_truth = {}
source_hashes = {}
maximum_error = 0.0
for seed in protocol["seeds"]:
    run = root / f"seed-{seed:02d}"
    assert (
        json.loads((root / f"seed-{seed:02d}-exit.json").read_text())["exit_code"] == 0
    )
    audit = json.loads((root / f"seed-{seed:02d}-input-audit.json").read_text())
    assert audit["folds"] == 5 and audit["exact_input_cells"] == size * 151 * 5
    with (run / "packages.csv").open() as stream:
        packages = {r["Package"]: r["Version"] for r in csv.DictReader(stream)}
    assert all(packages[k] == primary_packages[k] for k in relevant)
    with (run / "metrics.csv").open() as stream:
        metrics = list(csv.DictReader(stream))
    assert len(metrics) == 5 and {r["parameter"] for r in metrics} == targets.keys()
    prediction_path = root / f"seed-{seed:02d}-prediction-audit/predictions.csv"
    with prediction_path.open() as stream:
        predictions = list(csv.DictReader(stream))
    assert len(predictions) == size * 5
    truth = {}
    groups = {(parameter, fold): [] for parameter in targets for fold in range(1, 6)}
    for row in predictions:
        key = (row["parameter"], int(row["fold"]), int(row["test_row"]))
        assert key not in truth and 1 <= key[2] <= size // 5
        values = tuple(float(row[k]) for k in ("truth", "prediction", "low", "high"))
        assert all(math.isfinite(v) for v in values) and values[2] <= values[3]
        truth[key] = values[0]
        groups[key[:2]].append(values)
    if seed == 1:
        reference_truth = truth
    else:
        assert truth == reference_truth
    for metric in metrics:
        assert (
            metric["method"] == "sabc_1d"
            and int(metric["size"]) == size
            and int(metric["seed"]) == seed
        )
        parameter = metric["parameter"]
        folds = [groups[parameter, fold] for fold in range(1, 6)]
        assert all(len(fold) == size // 5 for fold in folds)
        all_values = [v for fold in folds for v in fold]
        baseline_errors = []
        for index, fold in enumerate(folds):
            training_mean = statistics.fmean(
                v[0] for j, other in enumerate(folds) if j != index for v in other
            )
            baseline_errors.append(
                math.sqrt(statistics.fmean((v[0] - training_mean) ** 2 for v in fold))
            )
        baseline = statistics.fmean(baseline_errors)
        rmse = statistics.fmean(
            math.sqrt(statistics.fmean((v[1] - v[0]) ** 2 for v in fold))
            for fold in folds
        )
        calculated = {
            "rmse": rmse,
            "baseline_rmse": baseline,
            "performance": 1 - rmse / baseline,
            "coverage": statistics.fmean(v[2] <= v[0] <= v[3] for v in all_values),
            "interval_width": statistics.fmean(v[3] - v[2] for v in all_values),
        }
        for key, value in calculated.items():
            error = abs(value - float(metric[key]))
            assert math.isfinite(error) and error <= 1e-10, (
                seed,
                parameter,
                key,
                error,
            )
            maximum_error = max(maximum_error, error)
        checks.append({"seed": seed, "parameter": parameter, **calculated})
        scores.append(
            {
                "seed": seed,
                "parameter": parameter,
                "performance": calculated["performance"],
            }
        )
    for path in (
        run / "metrics.csv",
        run / "packages.csv",
        prediction_path,
        root / f"seed-{seed:02d}-exit.json",
        root / f"seed-{seed:02d}-input-audit.json",
    ):
        source_hashes[str(path.relative_to(root))] = hashlib.sha256(
            path.read_bytes()
        ).hexdigest()
summary = []
for parameter, target in targets.items():
    values = [r["performance"] for r in scores if r["parameter"] == parameter]
    summary.append(
        {
            "parameter": parameter,
            "published": target,
            "primary_seed_zero": primary[parameter],
            "seed_count": len(values),
            "mean": statistics.mean(values),
            "sample_sd": statistics.stdev(values),
            "minimum": min(values),
            "maximum": max(values),
            "published_within_observed_range": min(values) <= target <= max(values),
        }
    )
report = {
    "size": size,
    "seeds": protocol["seeds"],
    "summary": summary,
    "validated_predictions": size * 5 * len(protocol["seeds"]),
    "verified_input_cells": size * 151 * 5 * len(protocol["seeds"]),
    "independent_arithmetic_maximum_absolute_error": maximum_error,
    "arithmetic_absolute_tolerance": 1e-10,
    "matched_primary_package_versions": {k: primary_packages[k] for k in relevant},
    "scope": "Fixed-data estimator sensitivity. Observed ranges are not confidence intervals. No historical RNG identification, equivalence, primary-score replacement, or paper completion.",
}
args.output.mkdir(parents=True)
for name, value in (
    ("summary", report),
    ("source-hashes", source_hashes),
    ("arithmetic", checks),
):
    (args.output / f"{name}.json").write_text(json.dumps(value, indent=2) + "\n")
with (args.output / "scores.csv").open("w") as stream:
    writer = csv.DictWriter(stream, fieldnames=("seed", "parameter", "performance"))
    writer.writeheader()
    writer.writerows(scores)
print(json.dumps(report, indent=2))
