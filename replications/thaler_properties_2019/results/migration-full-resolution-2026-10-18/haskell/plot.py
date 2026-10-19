"""Show complete temporal resolution and retained ten-step subsamples."""

import json
from pathlib import Path

import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt

root = Path(__file__).resolve().parent
a = {p["case"]: p for p in json.loads((root / "audit.json").read_text())["cases"]}

arrays = []
for name in ["migration", "migration_vision15"]:
    values = np.asarray([p["diagonal_agent_counts"] for p in a[name]["profiles"]])
    assert values.shape == (1001, 101)
    arrays.append(values)
maximum = 18
assert max(int(v.max()) for v in arrays) <= maximum
plt.rcParams.update({"font.size": 9})
fig, axes = plt.subplots(2, 2, figsize=(11, 8))
fig.subplots_adjust(
    left=0.08, right=0.86, bottom=0.08, top=0.90, wspace=0.28, hspace=0.30
)
for row, (name, values) in enumerate(
    zip(["Vision 1–10", "Vision 1–15"], arrays, strict=True)
):
    for col, stop in enumerate([200, 1000]):
        ax = axes[row, col]
        im = ax.imshow(
            values[: stop + 1],
            origin="lower",
            aspect="auto",
            interpolation="nearest",
            extent=[-0.25, 50.25, -0.5, stop + 0.5],
            vmin=0,
            vmax=maximum,
            cmap="viridis",
        )
        ax.set(
            title=f"{name}, every step through {stop}",
            xlabel="Diagonal position",
            ylabel="Step",
            xlim=(0, 50),
            ylim=(0, stop),
        )
fig.colorbar(
    im, cax=fig.add_axes([0.90, 0.10, 0.02, 0.78]), label="Agents per diagonal bin"
)
fig.suptitle("Corrected Haskell migration: every-step observation", fontsize=12)
fig.savefig(root / "profiles.png", dpi=180)
fig.savefig(root / "profiles.pdf")
(root / "sampling-audit.json").write_text(
    json.dumps(
        {
            "full_frames_per_case": 1001,
            "prior_frames_per_case": 101,
            "prior_spatial_frames_exact": 101,
            "color_range": [0, maximum],
            "agent_observations": sum(x["agent_observations"] for x in a.values()),
            "scope": "Temporal visualization of existing runs, not additional seeds or a wave criterion.",
        },
        indent=2,
    )
    + "\n"
)
