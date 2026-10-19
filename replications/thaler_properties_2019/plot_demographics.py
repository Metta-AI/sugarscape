"""Plot all audited inheritance pairs without treating approximate targets as bounds."""

import argparse
import hashlib
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("audit", type=Path)
parser.add_argument("output", type=Path)
args = parser.parse_args()
report = json.loads(args.audit.read_text())
assert report["complete_ensemble"] and report["validated_pairs"] == 100
assert report["only_dynamics_difference"] == "I rule active (inheritance):"
assert [row["index"] for row in report["results"]] == list(range(100))
keys = ["mating", "inheritance"]
labels = ["Without inheritance", "With inheritance"]
colors = ["#2874a6", "#c35a18"]
comparisons = {row["metric"]: row for row in report["comparisons"]}
assert comparisons["final_sugar_gini"]["status"] == "defined"
fig, axes = plt.subplots(1, 2, figsize=(12, 4.8))
for key, label, color in zip(keys, labels, colors):
    trajectories = np.asarray(
        [row["scenarios"][key]["population_trajectory"] for row in report["results"]]
    )
    assert trajectories.shape == (100, 1001)
    lower, upper = np.percentile(trajectories, [5, 95], axis=0)
    axes[0].fill_between(range(1001), lower, upper, color=color, alpha=0.15)
    axes[0].plot(trajectories.mean(axis=0), color=color, label=label)
axes[0].set(
    xlabel="Simulation step", ylabel="Population", title="All 100 paired trajectories"
)
axes[0].legend(frameon=False)
axes[0].text(
    0.02,
    0.98,
    "Bands: 5th–95th run percentiles",
    transform=axes[0].transAxes,
    va="top",
    fontsize=9,
)
for row in report["results"]:
    values = [row["scenarios"][key]["metrics"]["final_sugar_gini"] for key in keys]
    assert all(value is not None for value in values)
    axes[1].plot([0, 1], values, color="#999999", alpha=0.25, linewidth=0.6)
    axes[1].scatter([0, 1], values, c=colors, s=8, alpha=0.5)
for index, key in enumerate(keys):
    estimate = comparisons["final_sugar_gini"]["estimates"][key]
    mean = estimate["mean"]
    low, high = estimate["ci95"]
    axes[1].errorbar(
        index,
        mean,
        yerr=[[mean - low], [high - mean]],
        fmt="o",
        color="black",
        capsize=5,
        markersize=6,
        zorder=5,
    )
for index, target in enumerate([0.21, 0.35]):
    axes[1].hlines(
        target, index - 0.25, index + 0.25, colors=colors[index], linestyles="dashed"
    )
    axes[1].text(
        index,
        target - 0.035,
        f"Appendix ≈{target}",
        ha="center",
        fontsize=9,
        color=colors[index],
    )
axes[1].axhline(0.7, color="#555555", linestyle=":")
axes[1].text(
    0.5, 0.715, "Book reference: 0.7 (not this paper's result)", ha="center", fontsize=9
)
axes[1].set(
    xticks=[0, 1],
    xticklabels=labels,
    ylabel="Sugar-wealth Gini",
    ylim=(0, 0.8),
    xlim=(-0.4, 1.4),
    title="Step 1,000: all pairs and mean 95% intervals",
)
for axis in axes:
    axis.spines[["top", "right"]].set_visible(False)
fig.suptitle("Thaler–Siebers inheritance replication: released source", fontsize=13)
fig.text(
    0.5,
    0.02,
    "Approximate appendix values are descriptive references, not equivalence bounds. Pointwise population bands are not confidence intervals.",
    ha="center",
    fontsize=9,
)
fig.tight_layout(rect=(0, 0.06, 1, 0.94))
args.output.mkdir(parents=True, exist_ok=False)
fig.savefig(args.output / "demographics.png", dpi=180)
fig.savefig(args.output / "demographics.pdf")
plt.close(fig)
(args.output / "provenance.json").write_text(
    json.dumps(
        {
            "audit_sha256": hashlib.sha256(args.audit.read_bytes()).hexdigest(),
            "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            "pairs": 100,
            "scope": "Complete original-source inheritance cohort only; no whole-paper verdict.",
        },
        indent=2,
    )
    + "\n"
)
