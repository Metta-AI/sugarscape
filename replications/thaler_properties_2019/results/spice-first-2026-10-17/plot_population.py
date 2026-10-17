"""Plot two audited single-seed spice trajectories, without ensemble inference."""

import csv
import gzip
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

root = Path(__file__).resolve().parent
fig, ax = plt.subplots(figsize=(7, 4))
for name, label in [
    (
        "first/spice_book/000-602352629/trajectory.summary.csv.gz",
        "Book ranges: vision 1–10, metabolisms 1–5",
    ),
    ("control-summary.csv.gz", "NetLogo-like ranges: vision 1–6, metabolisms 1–4"),
]:
    with gzip.open(root / name, "rt") as stream:
        rows = list(csv.DictReader(stream))
    assert [int(r["time"]) for r in rows] == list(range(1001))
    ax.plot(
        [int(r["time"]) for r in rows],
        [int(r["population"]) for r in rows],
        label=label,
    )
ax.set(
    xlabel="Simulation step",
    ylabel="Population",
    xlim=(0, 1000),
    ylim=(0, 420),
    title="Spice configurations — seed 602352629",
)
ax.legend(fontsize=8)
fig.text(
    0.5,
    0.01,
    "One original-source trajectory per setting; not an ensemble result.",
    ha="center",
    fontsize=9,
)
fig.tight_layout(rect=(0, 0.04, 1, 1))
fig.savefig(root / "population.png", dpi=180)
plt.close(fig)
