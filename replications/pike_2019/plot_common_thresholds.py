"""Plot the complete native threshold comparison without implying numerical validity."""

import argparse
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("comparison", type=Path)
parser.add_argument("output", type=Path)
args = parser.parse_args()
data = json.loads(args.comparison.read_text())
assert data["conditions"] == 400
assert not args.output.exists()
fig, axes = plt.subplots(1, 2, figsize=(11, 4), sharex=True, sharey=True)
for ax, variant, title in zip(
    axes, ["common-one", "common-multi"], ["One level", "Multiple levels"]
):
    for threshold, color in [(10, "#355c9a"), (5, "#c46024")]:
        row = next(
            r
            for r in data["histograms"]
            if r["construction"] == "common_edges"
            and r["variant"] == variant
            and r["threshold"] == threshold
        )
        ax.stairs(
            row["counts"],
            row["edges"],
            color=color,
            label=f"Threshold {threshold}: {row['defined_steps']:,} defined steps",
        )
    ax.set(title=title, xlabel="Sample standard deviation of log prices")
    ax.legend(fontsize=8)
    ax.grid(alpha=0.2)
axes[0].set_ylabel("Step count (500 common bins)")
fig.suptitle("Released implementation: full threshold comparison", fontsize=13)
fig.text(
    0.5,
    0.01,
    "All 400 runs contain nonfinite holdings. Undefined dispersion steps are omitted, not set to zero.",
    ha="center",
    fontsize=9,
)
fig.tight_layout(rect=(0, 0.05, 1, 0.94))
fig.savefig(args.output, dpi=180)
plt.close(fig)
