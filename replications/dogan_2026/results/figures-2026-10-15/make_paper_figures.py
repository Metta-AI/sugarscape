"""
make_paper_figures.py — generate the paper's two figures from the canonical
Stage 5 sweep (results/canonical/part_b_stage5_main.csv).

Figure 1: Gini@300 vs automation speed, one line per policy cell — the Gini
          inversion (means-tested cells migrate from lowest to highest).
Figure 2: cumulative deaths from resource exhaustion vs automation speed — the
          welfare ranking, stable across speeds (means-tested cells stay lowest,
          no-intervention baseline stays highest).

Both read the same five-seed means that produce Tables 2 and 4, so the figures
and tables are guaranteed consistent. Outputs -> results/canonical/*.png.
"""
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

OUT = Path("results/canonical")
df = pd.read_csv(OUT / "part_b_stage5_main.csv")

SPEEDS = ["slow", "balanced", "fast"]
SPEED_LABELS = ["slow\n(k=20, m=10)", "balanced\n(k=10, m=10)", "fast\n(k=5, m=20)"]

# cell_label (matches the CSV) -> (US-spelling legend label, per-line style).
# Every series gets a distinct colour + linestyle + marker so all seven are
# distinguishable; the baseline and the two means-tested cells are emphasised
# (heavier weight, higher z-order) because they carry the paper's argument.
CELLS = [
    ("baseline",               "no intervention",
     dict(color="#1f4e79", lw=2.6, ls="-",  marker="s", ms=7, zorder=6)),
    ("labour/ubi",             "labor / UBI",
     dict(color="#e69f00", lw=1.7, ls="--", marker="^", ms=6, zorder=3)),
    ("wealth/ubi",             "wealth / UBI",
     dict(color="#009e73", lw=1.7, ls="-.", marker="D", ms=5, zorder=3)),
    ("uhi_scenario",           "UHI scenario",
     dict(color="#7b3ff2", lw=1.7, ls=":",  marker="*", ms=9, zorder=3)),
    ("disp_levy/means_tested", "disp-levy / means-tested",
     dict(color="#8c564b", lw=1.7, ls=(0, (3, 1, 1, 1)), marker="P", ms=6, zorder=3)),
    ("labour/means_tested",    "labor / means-tested",
     dict(color="#d62728", lw=2.6, ls="--", marker="o", ms=7, zorder=5)),
    ("wealth/means_tested",    "wealth / means-tested",
     dict(color="#a01722", lw=2.6, ls="-",  marker="o", ms=7, zorder=5)),
]


def series(metric):
    g = df.groupby(["cell_label", "km_label"])[metric].mean().unstack("km_label")
    return g[SPEEDS]


def make_figure(metric, ylabel, title, fname, legend_loc):
    g = series(metric)
    fig, ax = plt.subplots(figsize=(6.4, 4.5))
    x = range(len(SPEEDS))
    for cell, label, st in CELLS:
        y = g.loc[cell].values
        ax.plot(x, y, label=label, **st)
    ax.set_xticks(list(x))
    ax.set_xticklabels(SPEED_LABELS)
    ax.set_xlabel("automation speed")
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.margins(x=0.08)
    ax.grid(True, axis="y", ls=":", alpha=0.5)
    ax.legend(fontsize=7.5, loc=legend_loc, framealpha=0.9, ncol=1)
    fig.tight_layout()
    fig.savefig(OUT / fname, dpi=200, bbox_inches="tight")
    plt.close(fig)
    print(f"wrote {OUT / fname}")


make_figure(
    "gini_final",
    "Gini coefficient at step 300",
    "Distributional ranking inverts with automation speed",
    "fig_gini_inversion.png",
    legend_loc="upper left",
)
make_figure(
    "starvation_deaths_total",
    "cumulative deaths from resource exhaustion",
    "Welfare ranking is stable across automation speed",
    "fig_welfare_robustness.png",
    legend_loc="center right",
)
