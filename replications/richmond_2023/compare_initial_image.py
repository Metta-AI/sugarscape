"""Compare released initial-image cell colors with two frozen host initializations."""

import argparse
import csv
import hashlib
import json
from pathlib import Path

from PIL import Image
import matplotlib.pyplot as plt
import numpy as np

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("image", type=Path)
parser.add_argument("gnu", type=Path)
parser.add_argument("clang", type=Path)
parser.add_argument("output", type=Path)
args = parser.parse_args()
assert not args.output.exists()
pixels = np.asarray(Image.open(args.image).convert("RGB"), dtype=np.float64)
assert pixels.shape == (1359, 1359, 3)
centers = ((np.arange(256) + 0.5) * 1359 / 256).astype(int)
samples = pixels[np.ix_(centers, centers)]
assert np.all(samples.sum(axis=2) > 0)
samples /= samples.sum(axis=2)[:, :, None]
palette = plt.get_cmap("viridis", 5)(np.arange(5))[:, :3]
palette /= palette.sum(axis=1)[:, None]
distance = ((samples[:, :, None, :] - palette[None, None, :, :]) ** 2).sum(axis=3)
ordered = np.sort(distance, axis=2)
assert np.all(ordered[:, :, 1] > ordered[:, :, 0])
classes = np.argmin(distance, axis=2)
results = []
for label, path in [
    ("GNU C++16/libstdc++", args.gnu),
    ("Apple Clang/libc++", args.clang),
]:
    with path.open() as stream:
        rows = [{k: int(v) for k, v in row.items()} for row in csv.DictReader(stream)]
    assert [(r["x"], r["y"]) for r in rows] == [
        (x, y) for x in range(256) for y in range(256)
    ]
    terrain = np.array([r["cell_capacity"] for r in rows]).reshape(256, 256)
    # CSV is x-major with ascending y; raster rows descend from the top of the view.
    projected = terrain.T[::-1, :]
    results.append(
        {
            "runtime": label,
            "states_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            "occupied_cells": sum(r["status"] == 1 for r in rows),
            "matching_cell_center_classes": int(np.count_nonzero(projected == classes)),
            "different_cell_center_classes": int(
                np.count_nonzero(projected != classes)
            ),
        }
    )
report = {
    "image_sha256": hashlib.sha256(args.image.read_bytes()).hexdigest(),
    "image_size": [1359, 1359],
    "cell_grid": [256, 256],
    "sampling": "Cell centers at floor((i+0.5)*1359/256); normalized RGB removes multiplicative lighting intensity; nearest of five Viridis color classes. No fitted crop, palette, seed or model parameter.",
    "orientation": "Original x-major capacity array transposed; reverse y to place maximum y at raster top.",
    "minimum_squared_distance_margin": float(
        np.min(ordered[:, :, 1] - ordered[:, :, 0])
    ),
    "comparisons": results,
    "interpretation": "Exact categorical initial-landscape reproduction for the Clang/libc++ extraction; not pixel identity, evidence of historical compiler identity, GPU-state parity, or validation of subsequent steps.",
    "future_gate": "Compare original-engine initial states separately. Do not replace the quantitative benchmark initialization to make it match the older visualization image.",
}
args.output.write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps(report))
assert results[1]["matching_cell_center_classes"] == 65536
