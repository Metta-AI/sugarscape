"""Plot finite-window price summaries, preserving per-run missingness."""

import argparse
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("analysis", type=Path)
parser.add_argument("output", type=Path)
args = parser.parse_args()
a = json.loads((args.analysis / "analysis.json").read_text())
assert a["runs"] == 2100 and a["step_records"] == 2100000
conditions = [
    "phase1-standard",
    "explicit-10-none",
    "explicit-10-released",
    "network-10-none",
    "network-10-released",
]
labels = [
    "Standard",
    "Explicit: no policy",
    "Explicit: released policy",
    "Network: no policy",
    "Network: released policy",
]
fig, axes = plt.subplots(1, 2, figsize=(11, 4.3), sharey=True)
for ax, metric, title in zip(
    axes,
    ["abs_log_geometric_mean", "sample_sd_log_price"],
    [
        "Distance from price one\n|log(geometric mean price)|",
        "Within-step price dispersion\nsample SD(log price)",
    ],
    strict=True,
):
    for window, offset, color, label in [
        ("early", -0.12, "#2671b8", "Early: steps 1–100"),
        ("late", 0.12, "#cb581b", "Late: steps 901–1000"),
    ]:
        rows = [
            next(
                r
                for r in a["estimates"]
                if r["condition"] == c
                and r["metric"] == metric
                and r["window"] == window
            )
            for c in conditions
        ]
        means = np.array([r["mean"] for r in rows])
        errors = np.array(
            [
                [r["mean"] - r["low"] for r in rows],
                [r["high"] - r["mean"] for r in rows],
            ]
        )
        ax.errorbar(
            means,
            np.arange(len(rows)) + offset,
            xerr=errors,
            fmt="o",
            color=color,
            capsize=3,
            label=label,
        )
    ax.set_title(title, fontsize=11)
    ax.set_xlabel("Mean of defined per-run window means")
    ax.grid(axis="x", alpha=0.2)
    ax.set_xlim(left=0)
axes[0].set_yticks(range(len(labels)), labels)
axes[0].invert_yaxis()
axes[1].legend(fontsize=9)
fig.suptitle("Pike reconstruction: movement groups form after ten trades", fontsize=13)
fig.text(
    0.5,
    0.015,
    "100 seeds/condition; late defined runs vary: price 98–100, dispersion 88–100. Pointwise 95% t intervals.\nRetrospective finite windows; missing values excluded, not zero. No asymptotic convergence claim.",
    ha="center",
    fontsize=8,
)
fig.tight_layout(rect=(0, 0.10, 1, 0.95))
args.output.mkdir(parents=True, exist_ok=False)
for extension in ["png", "pdf"]:
    fig.savefig(args.output / f"convergence.{extension}", dpi=180)
