"""Plot all prespecified gradient estimates and pointwise uncertainty."""

import json
from pathlib import Path
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

comparison = json.loads(Path(sys.argv[1]).read_text())["results"]
output = Path(sys.argv[2])
figure, axes = plt.subplots(2, 3, figsize=(13, 7), sharex=True)
for axis, parameter in zip(
    axes.flat, ["p1", "p3", "m_alpha", "m_beta", "w_alpha", "w_beta"], strict=True
):
    selected = [row for row in comparison if row["parameter"] == parameter]
    for kind, step, color, label in [
        ("ad", 0.001, "black", "AD"),
        ("fd", 0.001, "#0072B2", "FD h=.001"),
        ("fd", 0.01, "#D55E00", "FD h=.01"),
        ("fd", 0.05, "#009E73", "FD h=.05"),
    ]:
        rows = sorted(
            [row for row in selected if row["step"] == step],
            key=lambda row: row["time"],
        )
        axis.plot(
            [row["time"] for row in rows],
            [row[kind]["mean"] for row in rows],
            color=color,
            label=label,
            linewidth=1.3,
        )
        axis.fill_between(
            [row["time"] for row in rows],
            [row[kind]["ci95"][0] for row in rows],
            [row[kind]["ci95"][1] for row in rows],
            color=color,
            alpha=0.1,
        )
    axis.set_title(parameter)
    axis.axhline(0, color="gray", linewidth=0.5)
    axis.set_xlabel("Transition (0 = initialization)")
    axis.set_ylabel("Derivative of mean recorded wealth")
axes[0, 0].legend(fontsize=8)
figure.suptitle(
    "Quera reconstructed protocol: 256 independent seeds\nMeans and pointwise 95% intervals; not the published Figure 11 protocol"
)
figure.tight_layout()
figure.savefig(output, dpi=150)
