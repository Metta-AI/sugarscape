"""Plot complete audited spice cohorts with pointwise confidence intervals."""

import json
from pathlib import Path

import matplotlib
import numpy as np
from scipy import stats

matplotlib.use("Agg")
import matplotlib.pyplot as plt

root = Path(__file__).resolve().parent
report = json.loads((root / "ensemble-full-audit-001.json").read_text())
assert report["complete_ensemble"] and report["validated_pairs"] == 100
fig, axes = plt.subplots(1, 2, figsize=(11, 4))
times = np.arange(1001)
for key, label in [
    ("spice_book", "Book settings"),
    ("trade_off", "NetLogo-like settings"),
]:
    values = np.array(
        [r["scenarios"][key]["population_trajectory"] for r in report["results"]]
    )
    assert values.shape == (100, 1001)
    mean = values.mean(axis=0)
    margin = stats.t.ppf(0.975, 99) * stats.sem(values, axis=0)
    for ax in axes:
        (line,) = ax.plot(times, mean, label=label)
        ax.fill_between(
            times, mean - margin, mean + margin, color=line.get_color(), alpha=0.2
        )
axes[0].set(
    xlim=(0, 1000),
    ylim=(0, 410),
    title="Complete population trajectories",
    ylabel="Population",
)
axes[1].set(xlim=(500, 1000), ylim=(80, 120), title="Late trajectories")
for ax in axes:
    ax.set_xlabel("Simulation step")
    ax.legend(fontsize=8)
fig.suptitle("Original-source spice cohorts: 100 seeds per configuration")
fig.text(
    0.5,
    0.01,
    "Means and pointwise 95% intervals; no equivalence bounds for approximate appendix descriptions.",
    ha="center",
    fontsize=9,
)
fig.tight_layout(rect=(0, 0.04, 1, 0.94))
fig.savefig(root / "population.png", dpi=180)
fig.savefig(root / "population.svg")
svg = root / "population.svg"
svg.write_text("\n".join(line.rstrip() for line in svg.read_text().splitlines()) + "\n")
plt.close(fig)
