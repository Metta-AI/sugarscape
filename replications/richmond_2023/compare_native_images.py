"""Compare fixed-grid published visualization colors with native state reconstructions."""

import argparse
import gzip
import hashlib
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from PIL import Image
import numpy as np

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("snapshots", type=Path)
parser.add_argument("author_images", type=Path)
parser.add_argument("output", type=Path)
args = parser.parse_args()
with gzip.open(args.snapshots, "rt") as stream:
    capture = json.load(stream)
assert capture["coordinate_order"] == "x major, ascending y"
assert [s["step"] for s in capture["snapshots"]] == [-1, 0, 49]
args.output.mkdir(exist_ok=False)
palette = np.vstack([plt.get_cmap("viridis", 5)(np.arange(5))[:, :3], [1.0, 0.0, 0.0]])
normalized_palette = palette / palette.sum(axis=1)[:, None]
centers = ((np.arange(256) + 0.5) * 1359 / 256).astype(int)
fig, axes = plt.subplots(2, 3, figsize=(12, 8.8))
fig.subplots_adjust(
    left=0.02, right=0.98, bottom=0.07, top=0.91, wspace=0.05, hspace=0.12
)
reports = []
for col, (snapshot, name) in enumerate(
    zip(capture["snapshots"], ["0.png", "1.png", "50.png"])
):
    path = args.author_images / name
    pixels = np.asarray(Image.open(path).convert("RGB"), dtype=np.float64)
    assert pixels.shape == (1359, 1359, 3)
    samples = pixels[np.ix_(centers, centers)]
    assert np.all(samples.sum(axis=2) > 0)
    samples /= samples.sum(axis=2)[:, :, None]
    distances = (
        (samples[:, :, None, :] - normalized_palette[None, None, :, :]) ** 2
    ).sum(axis=3)
    ordered = np.sort(distances, axis=2)
    assert np.all(ordered[:, :, 1] > ordered[:, :, 0])
    author = np.argmin(distances, axis=2)
    native = np.array(snapshot["environment_sugar"]).reshape(256, 256).T[::-1, :]
    assert set(np.unique(native)) <= set(range(-1, 5))
    native = np.where(native == -1, 5, native)
    confusion = np.zeros((6, 6), dtype=int)
    np.add.at(confusion, (author.ravel(), native.ravel()), 1)
    assert confusion.sum() == 65536
    report = {
        "iteration": snapshot["step"] + 1,
        "source_image_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "exact_cell_color_class_matches": int(np.count_nonzero(author == native)),
        "different_cell_color_classes": int(np.count_nonzero(author != native)),
        "author_red_cells": int(np.count_nonzero(author == 5)),
        "native_red_cells": int(np.count_nonzero(native == 5)),
        "shared_red_coordinates": int(np.count_nonzero((author == 5) & (native == 5))),
        "confusion_rows_author_columns_native_classes_0to4_then_red": confusion.tolist(),
        "minimum_squared_distance_margin": float(
            np.min(ordered[:, :, 1] - ordered[:, :, 0])
        ),
    }
    reports.append(report)
    axes[0, col].imshow(pixels.astype(np.uint8))
    axes[1, col].imshow(palette[native], interpolation="nearest")
    axes[0, col].set_title(f"Author image: iteration {snapshot['step'] + 1}")
    axes[1, col].set_title(f"Native reconstruction: iteration {snapshot['step'] + 1}")
    for ax in axes[:, col]:
        ax.set_axis_off()
fig.suptitle(
    "Figure 11 D–F: original released images versus audited H100 run", fontsize=14
)
fig.text(
    0.5,
    0.025,
    "Viridis: environment sugar 0–4; red: original −1 sentinel. Empty-cell resources reconstructed; no fitted crop or seed.",
    ha="center",
    fontsize=10,
)
fig.savefig(args.output / "comparison.png", dpi=150)
fig.savefig(args.output / "comparison.pdf")
plt.close(fig)
report = {
    "snapshot_sha256": hashlib.sha256(args.snapshots.read_bytes()).hexdigest(),
    "method": "Same fixed1359-square image grid, 256 cell centers, normalizedRGB and source Viridis5/red palette for every panel. Native x-major grid transposed and y reversed. No fitted crop,seed,orientation or palette.",
    "scope": "Native first/fiftieth active states audited; empty-cell resource values reconstructed from source accounting and observed movements, not directly GPU-captured. This does not reproduce OpenGL lighting or establish the historical visualization toolchain.",
    "comparisons": reports,
}
(args.output / "audit.json").write_text(json.dumps(report, indent=2) + "\n")
print(
    json.dumps(
        [{k: v for k, v in r.items() if not k.startswith("confusion")} for r in reports]
    )
)
