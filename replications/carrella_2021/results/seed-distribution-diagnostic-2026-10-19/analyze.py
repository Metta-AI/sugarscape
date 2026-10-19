"""Exploratory unpaired label permutation of the retained 64+64 seed ensemble."""

import argparse
import csv
import hashlib
import io
import json
from pathlib import Path

import numpy as np

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("runs", type=Path)
parser.add_argument("output", type=Path)
args = parser.parse_args()
assert not args.output.exists()
raw = args.runs.read_bytes()
rows = list(csv.DictReader(io.StringIO(raw.decode())))
assert len(rows) == 128
for variant in ["native", "independent"]:
    assert sorted(int(r["seed"]) for r in rows if r["variant"] == variant) == list(
        range(64)
    )
metrics = [
    "last_population",
    "minimum_population",
    "price_at475",
    "last_price",
    "maximum_price",
    "mean_price",
]
values = np.array([[float(r[m]) for m in metrics] for r in rows])
assert np.isfinite(values).all()
labels = np.array([r["variant"] == "native" for r in rows])
orders = np.argsort(values, axis=0, kind="stable")
sorted_values = np.take_along_axis(values, orders, axis=0)
ends = np.concatenate(
    [sorted_values[:-1] != sorted_values[1:], np.ones((1, len(metrics)), dtype=bool)]
)
# Evaluate empirical cumulative probabilities after every complete tie group.
observed = (
    np.max(
        np.where(
            ends,
            np.abs(2 * np.cumsum(labels[orders], axis=0) - np.arange(1, 129)[:, None]),
            0,
        ),
        axis=0,
    )
    / 64
)
# Independently check the observed statistic with direct threshold counting.
for column in range(len(metrics)):
    a = values[labels, column]
    b = values[~labels, column]
    direct = max(
        abs(np.count_nonzero(a <= t) - np.count_nonzero(b <= t)) / 64
        for t in np.unique(values[:, column])
    )
    assert direct == observed[column]
rng = np.random.default_rng(20261019)
repetitions = 19999
exceed = np.zeros(len(metrics), dtype=int)
joint_exceed = 0
for _ in range(repetitions):
    shuffled = rng.permutation(labels)
    statistic = (
        np.max(
            np.where(
                ends,
                np.abs(
                    2 * np.cumsum(shuffled[orders], axis=0) - np.arange(1, 129)[:, None]
                ),
                0,
            ),
            axis=0,
        )
        / 64
    )
    exceed += statistic >= observed
    joint_exceed += statistic.max() >= observed.max()
results = []
for i, metric in enumerate(metrics):
    results.append(
        {
            "metric": metric,
            "ecdf_maximum_difference": float(observed[i]),
            "permutation_exceedances": int(exceed[i]),
            "monte_carlo_p_plus_one": float((exceed[i] + 1) / (repetitions + 1)),
            "native_median": float(np.median(values[labels, i])),
            "independent_median": float(np.median(values[~labels, i])),
        }
    )
report = {
    "inputs_sha256": hashlib.sha256(raw).hexdigest(),
    "numpy": np.__version__,
    "seeds_per_engine": 64,
    "excluded_runs": 0,
    "permutation_seed": 20261019,
    "permutations": repetitions,
    "metrics": results,
    "joint_maximum_ecdf_difference": float(observed.max()),
    "joint_exceedances": int(joint_exceed),
    "joint_monte_carlo_p_plus_one": (joint_exceed + 1) / (repetitions + 1),
    "scope": "Exploratory post-hoc diagnostic at one parameter setting selected after estimator failures. Shared permutations preserve dependence across six metrics; ties retained. Seed labels are unpaired because engines use different random streams. Failure to detect a difference is not equivalence, historical reproduction, or a paper verdict.",
}
args.output.mkdir(parents=True)
(args.output / "summary.json").write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps(report, indent=2))
