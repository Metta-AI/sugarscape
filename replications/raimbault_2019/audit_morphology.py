"""Rebuild the published morphology projection and audit reference scaling."""

import argparse
import csv
import gzip
import hashlib
import json
from pathlib import Path
import subprocess

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("raw", type=Path)
parser.add_argument("reference", type=Path)
parser.add_argument("source", type=Path)
parser.add_argument("output", type=Path)
args = parser.parse_args()
assert (
    subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=args.source, text=True
    ).strip()
    == "270cc7f112b3a999b10e02b0f9525038d6d4754d"
)
assert not subprocess.check_output(
    ["git", "status", "--porcelain", "--untracked-files=no"], cwd=args.source, text=True
).strip()
assert (
    hashlib.sha256(args.raw.read_bytes()).hexdigest()
    == "26372b8698eefb1666ce8c6176f7188e55ced62fab795ff11a03cae564554199"
)
assert (
    hashlib.sha256(args.reference.read_bytes()).hexdigest()
    == "2fc276934c6c50994a2c24196b7da4231383ef3d13f86804b5c38cb0d1d93add"
)
features = ["distance", "entropy", "moran", "slope"]
components = ["PC1", "PC2", "PC3", "PC4"]
counts = np.zeros(50, dtype=np.int64)
sums = np.zeros((50, 4))
with gzip.open(args.raw, "rt", newline="") as stream:
    for row in csv.DictReader(stream):
        identity = int(row["id"])
        values = [float(row[k]) for k in features]
        assert 0 <= identity < 50 and np.isfinite(values).all()
        counts[identity] += 1
        sums[identity] += values
assert int(counts.sum()) == 2727994 and (counts > 0).all()
means = sums / counts[:, None]
low, high = means.min(axis=0), means.max(axis=0)
normalized = (means - low) / (high - low)
folder = args.source / "sugarscape/exploration"
paths = [
    folder / "20170328_gridsynth_morphopca.csv",
    folder / "20170328_gridsynth_rotation.csv",
    args.source / "sugarscape/comp.R",
    args.source / "sugarscape/metaphasediagrams.R",
]
with paths[0].open() as stream:
    archived = list(csv.DictReader(stream))
assert [int(r["id"]) for r in archived] == list(range(50))
archived_normalized = np.array([[float(r[k]) for k in features] for r in archived])
archived_scores = np.array([[float(r[k]) for k in components] for r in archived])
with paths[1].open() as stream:
    rotations = list(csv.DictReader(stream))
assert [r[""] for r in rotations] == features
archived_rotation = np.array([[float(r[k]) for k in components] for r in rotations])
_, singular, vh = np.linalg.svd(
    normalized - normalized.mean(axis=0), full_matrices=False
)
rotation = vh.T
rotation *= np.sign((rotation * archived_rotation).sum(axis=0))
# Preserve the author's uncentered projection; centering would translate all points.
scores = normalized @ rotation
errors = {
    "normalized_features": float(abs(normalized - archived_normalized).max()),
    "rotation": float(abs(rotation - archived_rotation).max()),
    "scores": float(abs(scores - archived_scores).max()),
}
assert max(errors.values()) < 1e-10
with args.reference.open() as stream:
    reference_rows = list(csv.DictReader(stream))
assert len(reference_rows) == 55000
reference = np.array([float(reference_rows[0][k]) for k in features])
assert all(
    [float(row[k]) for k in features] == reference.tolist() for row in reference_rows
)
original_point = reference @ archived_rotation
consistent_point = ((reference - low) / (high - low)) @ archived_rotation
assert np.max(abs(original_point[:2] - [1.130869, 0.09586869])) < 5e-7
variance = singular**2 / np.sum(singular**2)
report = {
    "raw_rows": int(counts.sum()),
    "landscapes": 50,
    "reference_rows": len(reference_rows),
    "features": features,
    "counts": counts.tolist(),
    "raw_means": means.tolist(),
    "feature_minima": low.tolist(),
    "feature_maxima": high.tolist(),
    "max_errors": errors,
    "variance_fractions": variance.tolist(),
    "first_two_variance_percent": float(100 * variance[:2].sum()),
    "published_percent": 92,
    "rounded_percent_matches": round(float(100 * variance[:2].sum())) == 92,
    "reference_raw": reference.tolist(),
    "released_reference_projection": original_point.tolist(),
    "consistently_scaled_reference_projection": consistent_point.tolist(),
    "source_sha256": {
        str(p.relative_to(args.source)): hashlib.sha256(p.read_bytes()).hexdigest()
        for p in paths
    },
    "interpretation": "Released generated-grid coordinates use min-max normalized features. Released reference marker multiplies raw features by the same rotation, omitting that normalization. Consistent scaling moves only this diagnostic marker; it does not change Table4 distances or simulated outcomes. Archived-data audit, not fresh simulation coverage or a whole-paper verdict.",
}
args.output.mkdir(parents=True, exist_ok=False)
(args.output / "audit.json").write_text(json.dumps(report, indent=2) + "\n")
fig, ax = plt.subplots(figsize=(7, 6))
ax.scatter(
    scores[:, 0], scores[:, 1], color="0.55", label="50 released generated grids"
)
ax.scatter(
    *original_point[:2],
    color="black",
    marker="o",
    s=75,
    label="Released reference marker",
)
ax.scatter(
    *consistent_point[:2],
    color="#b23b20",
    marker="X",
    s=95,
    label="Reference with same feature scaling",
)
ax.annotate(
    "",
    xy=consistent_point[:2],
    xytext=original_point[:2],
    arrowprops={"arrowstyle": "->", "color": "#b23b20"},
)
ax.set(
    xlabel="Principal component 1",
    ylabel="Principal component 2",
    title="Reference scaling diagnostic (archived data)",
)
ax.legend(fontsize=9, loc="upper left")
fig.tight_layout()
fig.savefig(args.output / "reference-scaling.png", dpi=170)
fig.savefig(args.output / "reference-scaling.pdf")
print(
    json.dumps(
        {
            k: report[k]
            for k in [
                "max_errors",
                "first_two_variance_percent",
                "released_reference_projection",
                "consistently_scaled_reference_projection",
            ]
        }
    )
)
