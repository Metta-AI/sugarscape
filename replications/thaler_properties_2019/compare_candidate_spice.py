"""Compare complete candidate and Haskell spice cohorts without pairing RNG seeds."""

import argparse
import hashlib
import json
from pathlib import Path

import matplotlib
import numpy as np
from scipy import stats

matplotlib.use("Agg")
import matplotlib.pyplot as plt

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("candidate", type=Path)
parser.add_argument("original", type=Path)
parser.add_argument("corrected", type=Path)
parser.add_argument("output", type=Path)
args = parser.parse_args()
paths = {name: getattr(args, name) for name in ["candidate", "original", "corrected"]}
reports = {name: json.loads(path.read_text()) for name, path in paths.items()}
trajectories = {}
for name, report in reports.items():
    assert report["complete_ensemble"]
    rows = report["results"]
    assert len(rows) == 100 and [r["index"] for r in rows] == list(range(100))
    assert len({r["seed"] for r in rows}) == 100
    if name == "candidate":
        assert report["validated_unique_inputs"] == 100
        values = [r["population_trajectory"] for r in rows]
    else:
        protocol_bytes = (paths[name].parent / "protocol.json").read_bytes()
        assert hashlib.sha256(protocol_bytes).hexdigest() == report["protocol_sha256"]
        protocol = json.loads(protocol_bytes)
        assert list(protocol["variants"]) == [name] and report["validated_pairs"] == 100
        values = [r["scenarios"]["trade_off"]["population_trajectory"] for r in rows]
    trajectories[name] = np.asarray(values, dtype=float)
    assert trajectories[name].shape == (100, 1001)
    assert np.isfinite(trajectories[name]).all()
    assert (trajectories[name][:, 0] == 400).all()
    assert (np.diff(trajectories[name], axis=1) <= 0).all()

comparisons = []
for metric, selection in [
    ("at100", 100),
    ("at500", 500),
    ("at1000", 1000),
    ("late801_1000", slice(801, 1001)),
]:
    samples = {name: values[:, selection] for name, values in trajectories.items()}
    if isinstance(selection, slice):
        samples = {name: values.mean(axis=1) for name, values in samples.items()}
    estimates = {}
    for name, values in samples.items():
        mean = float(values.mean())
        margin = float(stats.t.ppf(0.975, 99) * stats.sem(values))
        estimates[name] = {
            "n": 100,
            "mean": mean,
            "ci95": [mean - margin, mean + margin],
        }
    differences = {}
    for name in ["original", "corrected"]:
        left, right = samples[name], samples["candidate"]
        variances = np.array([left.var(ddof=1), right.var(ddof=1)]) / 100
        degrees = float(variances.sum() ** 2 / ((variances**2).sum() / 99))
        mean = float(left.mean() - right.mean())
        margin = float(stats.t.ppf(0.975, degrees) * np.sqrt(variances.sum()))
        differences[name + "_minus_candidate"] = {
            "mean": mean,
            "welch_degrees_of_freedom": degrees,
            "ci95": [mean - margin, mean + margin],
        }
    comparisons.append(
        {"metric": metric, "estimates": estimates, "differences": differences}
    )

args.output.mkdir(exist_ok=False)
result = {
    "input_sha256": {
        name: hashlib.sha256(path.read_bytes()).hexdigest()
        for name, path in paths.items()
    },
    "comparisons": comparisons,
    "scope": "Independent-cohort Welch intervals; identical integer seeds are not paired initial states across RNG implementations. Pointwise, not simultaneous or equivalence intervals. Candidate 2009 source identity unverified; no whole-paper verdict.",
}
(args.output / "comparison.json").write_text(
    json.dumps(result, indent=2, allow_nan=False) + "\n"
)
figure, axes = plt.subplots(1, 2, figsize=(12, 4), constrained_layout=True)
labels = {
    "candidate": "NetLogo candidate",
    "original": "Haskell released",
    "corrected": "Haskell corrected",
}
for name, values in trajectories.items():
    mean = values.mean(axis=0)
    margin = stats.t.ppf(0.975, 99) * stats.sem(values, axis=0)
    for axis in axes:
        (line,) = axis.plot(np.arange(1001), mean, label=labels[name])
        axis.fill_between(
            np.arange(1001),
            mean - margin,
            mean + margin,
            color=line.get_color(),
            alpha=0.15,
        )
for axis, limits in zip(axes, [(0, 100), (100, 1000)], strict=True):
    axis.set_xlim(*limits)
    axis.set_xlabel("Simulation step")
    axis.set_ylabel("Mean surviving population")
    axis.grid(alpha=0.2)
axes[0].set_ylim(80, 410)
axes[1].set_ylim(80, 145)
axes[1].legend()
figure.suptitle(
    "Matched spice settings: 100 inputs per implementation; pointwise 95% intervals"
)
figure.savefig(args.output / "population.png", dpi=150)
figure.savefig(args.output / "population.svg")
plt.close(figure)
print(json.dumps(result))
