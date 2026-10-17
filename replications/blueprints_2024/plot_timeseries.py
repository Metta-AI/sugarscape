"""Plot audited complete-model means; no cross-model or paper-figure verdict."""

import argparse
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("evidence", type=Path)
args = parser.parse_args()
audit = json.loads((args.evidence / "audit.json").read_text())
assert audit["runs"] == 500 and audit["timesteps"] == 5001
means = np.loadtxt(args.evidence / "independent-means.csv", delimiter=",", skiprows=1)
derived = np.loadtxt(args.evidence / "derived-means.csv", delimiter=",", skiprows=1)
assert means.shape == (5001, 7) and derived.shape == (5001, 3)
assert np.array_equal(means[:, 0], derived[:, 0])
fig, axes = plt.subplots(2, 3, figsize=(12, 7), layout="constrained")
series = [
    ("Population", means[:, 1]),
    ("Mean time to live", means[:, 2]),
    ("Starvation + combat deaths / population", derived[:, 1]),
    ("Mean age at death", means[:, 6]),
    ("Total wealth", means[:, 5]),
    ("Wealth / population", derived[:, 2]),
]
for axis, (label, values) in zip(axes.flat, series, strict=True):
    axis.plot(means[:, 0], values, color="#b67600", linewidth=1.4)
    axis.set(title=label, xlabel="Timestep", xlim=(0, 5000))
    axis.grid(alpha=0.2)
fig.suptitle(
    f"{audit['model']}: 500 original seeds\nEnsemble means; post-extinction rows contribute zero",
    fontsize=13,
)
fig.savefig(args.evidence / "timeseries.png", dpi=160)
fig.savefig(args.evidence / "timeseries.pdf")
plt.close(fig)
