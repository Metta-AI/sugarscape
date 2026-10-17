"""Plot audited paired trade cohorts; bands are pointwise confidence intervals."""

import json
from pathlib import Path

import matplotlib
import numpy as np
from scipy import stats

matplotlib.use("Agg")
import matplotlib.pyplot as plt

root = Path(__file__).resolve().parent
report = json.loads((root / "full-paired-audit-001.json").read_text())
assert report["complete_ensemble"] and report["validated_pairs"] == 100
fig, axes = plt.subplots(1, 2, figsize=(11, 4))
times = np.arange(1001)
arrays = []
for key, label in [("trade_off", "Trade off"), ("trade_on", "Trade on")]:
    values = np.array(
        [r["scenarios"][key]["population_trajectory"] for r in report["results"]]
    )
    assert values.shape == (100, 1001)
    arrays.append(values)
    mean = values.mean(axis=0)
    margin = stats.t.ppf(0.975, 99) * stats.sem(values, axis=0)
    (line,) = axes[0].plot(times, mean, label=label)
    axes[0].fill_between(
        times, mean - margin, mean + margin, color=line.get_color(), alpha=0.2
    )
difference = arrays[1] - arrays[0]
mean = difference.mean(axis=0)
margin = stats.t.ppf(0.975, 99) * stats.sem(difference, axis=0)
axes[1].plot(times, mean, color="tab:green")
axes[1].fill_between(times, mean - margin, mean + margin, color="tab:green", alpha=0.2)
axes[1].axhline(0, color="black", linewidth=0.7)
axes[0].set(title="Population", ylabel="Agents", ylim=(0, 410))
axes[0].legend()
axes[1].set(title="Paired change: trade on minus off", ylabel="Agents")
for ax in axes:
    ax.set(xlabel="Simulation step", xlim=(0, 1000))
fig.suptitle("Original-source trade controls: 100 paired seeds")
fig.text(
    0.5,
    0.01,
    "Means and pointwise 95% intervals; released coordinate and observation defects remain.",
    ha="center",
    fontsize=9,
)
fig.tight_layout(rect=(0, 0.04, 1, 0.94))
fig.savefig(root / "population.png", dpi=180)
fig.savefig(root / "population.svg")
svg = root / "population.svg"
svg.write_text("\n".join(line.rstrip() for line in svg.read_text().splitlines()) + "\n")
plt.close(fig)
