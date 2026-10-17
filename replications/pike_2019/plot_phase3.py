"""Plot run-level survival estimates for movement and no-policy ensembles."""

import argparse
import hashlib
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("analysis", type=Path)
parser.add_argument("output", type=Path)
args = parser.parse_args()
raw = (args.analysis / "analysis.json").read_bytes()
report = json.loads(raw)
survivors = {
    e["condition"]: e["interval"]
    for e in report["estimates"]
    if e["metric"] == "survivors"
}
assert len(survivors) == 18
assert all(e["n"] == 100 for e in survivors.values())
fig, axes = plt.subplots(1, 2, figsize=(10, 4.5), sharey=True)
for ax, approach in zip(axes, ["explicit", "network"], strict=True):
    for selector, label, offset, color in [
        ("none", "No movement policy", -0.2, "#333333"),
        ("released", "Released selector", 0.0, "#0072B2"),
        ("corrected-highest", "Corrected selector (sensitivity)", 0.2, "#D55E00"),
    ]:
        estimates = [
            survivors[f"{approach}-{threshold}-{selector}"] for threshold in [1, 5, 10]
        ]
        means = [e["mean"] for e in estimates]
        ax.errorbar(
            [i + offset for i in range(3)],
            means,
            yerr=[
                [e["mean"] - e["low"] for e in estimates],
                [e["high"] - e["mean"] for e in estimates],
            ],
            fmt="o",
            capsize=3,
            color=color,
            label=label,
        )
    ax.set(
        title=approach.capitalize(),
        xlabel="Trade threshold",
        xticks=range(3),
        xticklabels=[1, 5, 10],
    )
    ax.grid(axis="y", alpha=0.2)
axes[0].set_ylabel("Individual survivors after 1,000 steps")
handles, labels = axes[0].get_legend_handles_labels()
fig.legend(handles, labels, loc="lower center", ncol=3, frameon=False, fontsize=8)
fig.suptitle("Pike movement experiment: new 100-seed ensembles")
fig.text(
    0.5,
    0.09,
    "Pointwise 95% intervals; corrected runs are sensitivity experiments, not historical replication.",
    ha="center",
    fontsize=8,
)
fig.tight_layout(rect=(0, 0.14, 1, 0.94))
args.output.mkdir(parents=True, exist_ok=False)
for extension in ["png", "pdf"]:
    fig.savefig(args.output / f"survivors.{extension}", dpi=180)
plt.close(fig)
(args.output / "provenance.json").write_text(
    json.dumps(
        {
            "analysis_sha256": hashlib.sha256(raw).hexdigest(),
            "plotter_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        },
        indent=2,
    )
    + "\n"
)
