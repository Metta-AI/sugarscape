"""Compare complete declared seed cohorts without pairing different random streams."""

import argparse
import csv
import hashlib
import io
import json
import math
from pathlib import Path

import numpy as np

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("protocol", type=Path)
parser.add_argument("runs", type=Path)
parser.add_argument("output", type=Path)
args = parser.parse_args()
assert not args.output.exists()
raw = args.runs.read_bytes()
rows = list(csv.DictReader(io.StringIO(raw.decode())))
protocol_bytes = args.protocol.read_bytes()
protocol = json.loads(protocol_bytes)
seeds = protocol["fresh_seeds"]
assert seeds and seeds == list(range(seeds[0], seeds[-1] + 1))
n = len(seeds)
assert protocol["native_runs"] == protocol["independent_runs"] == n
assert len(rows) == 2 * n
for variant in ["native", "independent"]:
    assert sorted(int(r["seed"]) for r in rows if r["variant"] == variant) == seeds
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
            np.abs(
                2 * np.cumsum(labels[orders], axis=0) - np.arange(1, 2 * n + 1)[:, None]
            ),
            0,
        ),
        axis=0,
    )
    / n
)
# Independently check the observed statistic with direct threshold counting.
for column in range(len(metrics)):
    a = values[labels, column]
    b = values[~labels, column]
    direct = max(
        abs(np.count_nonzero(a <= t) - np.count_nonzero(b <= t)) / n
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
                    2 * np.cumsum(shuffled[orders], axis=0)
                    - np.arange(1, 2 * n + 1)[:, None]
                ),
                0,
            ),
            axis=0,
        )
        / n
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
events = {}
for event in ["persistent_late_price", "low_final_population"]:
    counts = {}
    for variant in ["native", "independent"]:
        group = [r for r in rows if r["variant"] == variant]
        hits = (
            [
                int(r["seed"])
                for r in group
                if (float(r["price_at475"]) >= 10 and float(r["last_price"]) >= 10)
            ]
            if event == "persistent_late_price"
            else [int(r["seed"]) for r in group if float(r["last_population"]) < 50]
        )
        counts[variant] = {"count": len(hits), "rate": len(hits) / n, "seeds": hits}
    total_hits = counts["native"]["count"] + counts["independent"]["count"]
    support = range(max(0, total_hits - n), min(n, total_hits) + 1)
    weights = {
        x: math.comb(total_hits, x) * math.comb(2 * n - total_hits, n - x)
        for x in support
    }
    denominator = math.comb(2 * n, n)
    assert sum(weights.values()) == denominator
    observed_weight = weights[counts["native"]["count"]]
    numerator = sum(weight for weight in weights.values() if weight <= observed_weight)
    events[event] = {
        "counts": counts,
        "native_minus_independent_rate": (
            counts["native"]["count"] - counts["independent"]["count"]
        )
        / n,
        "two_sided_fisher_p": numerator / denominator,
    }
report = {
    "protocol_sha256": hashlib.sha256(protocol_bytes).hexdigest(),
    "rare_events": events,
    "inputs_sha256": hashlib.sha256(raw).hexdigest(),
    "numpy": np.__version__,
    "seeds_per_engine": n,
    "excluded_runs": 0,
    "permutation_seed": 20261019,
    "permutations": repetitions,
    "metrics": results,
    "joint_maximum_ecdf_difference": float(observed.max()),
    "joint_exceedances": int(joint_exceed),
    "joint_monte_carlo_p_plus_one": (joint_exceed + 1) / (repetitions + 1),
    "scope": "Single-parameter diagnostic; setting selected after estimator failures. Rare thresholds are prospective only for the separately registered extension, exploratory for earlier seeds. No multiplicity correction across rare-event tests and continuous-metric analysis. Shared permutations preserve dependence across six metrics; ties retained. Seed labels are unpaired because engines use different random streams. Failure to detect a difference is not equivalence, historical reproduction, or a paper verdict.",
}
args.output.mkdir(parents=True)
(args.output / "summary.json").write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps(report, indent=2))
