"""Reconstruct Figure 11 A-C data; compare hardware timings descriptively."""

import argparse
import csv
import hashlib
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("native", type=Path)
parser.add_argument("reference", type=Path)
parser.add_argument("output", type=Path)
args = parser.parse_args()
args.output.mkdir(exist_ok=False)
data = {}
hashes = {}
for label, root in [
    ("H100 / CUDA 11.8", args.native),
    ("Archived V100 / CUDA 11.0", args.reference),
]:
    data[label] = {}
    hashes[label] = {}
    for name in [
        "occupationperStep.csv",
        "resolution_steps.csv",
        "performance_scaling.csv",
    ]:
        path = root / name
        with path.open() as stream:
            data[label][name] = list(csv.DictReader(stream))
        hashes[label][name] = hashlib.sha256(path.read_bytes()).hexdigest()
labels = list(data)
densities = ["0.02", "0.04", "0.08", "0.16", "0.32", "0.64"]
fig, axes = plt.subplots(1, 3, figsize=(15, 4.4))
fig.subplots_adjust(left=0.06, right=0.99, bottom=0.18, top=0.85, wspace=0.34)
colors = plt.get_cmap("viridis")(np.linspace(0.05, 0.9, 6))
means = {"population": [], "resolution": [], "timing": []}
for density, color in zip(densities, colors):
    for name, steps, field in [
        ("occupationperStep.csv", 100, "pop_count"),
        ("resolution_steps.csv", 9, "mean_unresolved_count"),
    ]:
        samples = []
        for label in labels:
            subset = [r for r in data[label][name] if r["p_occupation"] == density]
            assert len(subset) == 3 * steps
            values = np.array([float(r[field]) for r in subset]).reshape(3, steps)
            if name == "resolution_steps.csv":
                values = (
                    values
                    / np.array([float(r["mean_pop_count"]) for r in subset]).reshape(
                        3, steps
                    )
                    * 100
                )
            samples.append(values)
        assert np.array_equal(*samples)
        values = samples[0]
        axis = axes[0] if steps == 100 else axes[1]
        x = np.arange(steps) if steps == 100 else np.arange(1, 10)
        axis.plot(x, values.mean(axis=0), color=color, label=density)
        axis.fill_between(
            x, values.min(axis=0), values.max(axis=0), color=color, alpha=0.15
        )
        key = "population" if steps == 100 else "resolution"
        means[key].append(
            {
                "density": density,
                "mean": values.mean(axis=0).tolist(),
                "minimum": values.min(axis=0).tolist(),
                "maximum": values.max(axis=0).tolist(),
            }
        )
for label, color in zip(labels, ["#0072B2", "#D55E00"]):
    rows = data[label]["performance_scaling.csv"]
    assert len(rows) == 48
    assert [(int(r["repetition"]), int(r["grid_width"])) for r in rows] == [
        (rep, w) for rep in range(3) for w in range(256, 4097, 256)
    ]
    times = np.array([float(r["s_step_mean"]) for r in rows]).reshape(3, 16)
    sizes = np.array([w * w for w in range(256, 4097, 256)])
    average = times.mean(axis=0)
    fit = np.polyfit(sizes, average, 1)
    predicted = np.polyval(fit, sizes)
    r_squared = (
        1 - ((average - predicted) ** 2).sum() / ((average - average.mean()) ** 2).sum()
    )
    axes[2].plot(sizes / 1e6, average * 1000, color=color, label=label)
    axes[2].fill_between(
        sizes / 1e6,
        times.min(axis=0) * 1000,
        times.max(axis=0) * 1000,
        color=color,
        alpha=0.2,
    )
    means["timing"].append(
        {
            "runtime": label,
            "cells": sizes.tolist(),
            "mean_seconds": average.tolist(),
            "minimum_seconds": times.min(axis=0).tolist(),
            "maximum_seconds": times.max(axis=0).tolist(),
            "linear_fit_all16_width_means": {
                "seconds_per_cell": float(fit[0]),
                "intercept_seconds": float(fit[1]),
                "r_squared": float(r_squared),
                "maximum_absolute_residual_seconds": float(
                    abs(average - predicted).max()
                ),
            },
        }
    )
axes[0].set(
    title="A  Reported population: exact archive agreement",
    xlabel="Simulation step",
    ylabel="Occupied agents (unresolved excluded)",
)
axes[1].set(
    title="B  Stored resolution bins: exact agreement",
    xlabel="Original CSV bin label",
    ylabel="Unresolved / mean occupied population (%)",
)
axes[2].set(
    title="C  Different GPU and toolchain",
    xlabel="Grid cells (millions)",
    ylabel="Mean step time (milliseconds)",
)
for ax in axes[:2]:
    ax.legend(title="Initial occupation", fontsize=7, ncol=2)
axes[2].legend(fontsize=7)
fig.suptitle(
    "Full original benchmark; lines are three-seed means, shading is seed minimum–maximum"
)
fig.savefig(args.output / "native-results.png", dpi=160)
fig.savefig(args.output / "native-results.pdf")
plt.close(fig)
report = {
    "sha256": hashes,
    "scope": "All 84 original conditions. Exact numerical comparisons for population and resolution. Timing fits are descriptive across all16 widths; no post-hoc acceptance threshold, hardware-equivalence claim or corrected-bin substitution. Shading is observed seed range, not a confidence interval.",
    "curves": means,
}
(args.output / "audit.json").write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps(means["timing"]))
