"""Compare every captured native frame without fitting image geometry or random seeds."""

import argparse
import gzip
import hashlib
import json
from pathlib import Path

import matplotlib
import numpy as np
from PIL import Image

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("snapshots", type=Path)
parser.add_argument("author_images", type=Path)
parser.add_argument("output", type=Path)
args = parser.parse_args()
assert not args.output.exists()
palette = np.vstack(
    [matplotlib.colormaps["viridis"].resampled(5)(np.arange(5))[:, :3], [1.0, 0.0, 0.0]]
)
normalized = palette / palette.sum(axis=1)[:, None]
centers = ((np.arange(256) + 0.5) * 1359 / 256).astype(int)
authors = {}
for name in ["0.png", "1.png", "50.png"]:
    path = args.author_images / name
    pixels = np.asarray(Image.open(path).convert("RGB"), dtype=np.float64)
    assert pixels.shape == (1359, 1359, 3)
    samples = pixels[np.ix_(centers, centers)]
    assert np.all(samples.sum(axis=2) > 0)
    samples /= samples.sum(axis=2)[:, :, None]
    distances = ((samples[:, :, None, :] - normalized[None, None, :, :]) ** 2).sum(
        axis=3
    )
    ordered = np.sort(distances, axis=2)
    assert np.all(ordered[:, :, 1] > ordered[:, :, 0])
    authors[name] = (
        np.argmin(distances, axis=2),
        hashlib.sha256(path.read_bytes()).hexdigest(),
    )
results = []
for variant in ["philox", "xorwow"]:
    path = args.snapshots / f"{variant}.snapshots.json.gz"
    with gzip.open(path, "rt") as stream:
        capture = json.load(stream)
    assert capture["coordinate_order"] == "x major, ascending y"
    assert [s["step"] for s in capture["snapshots"]] == list(range(-1, 100))
    for name, (author, image_hash) in authors.items():
        records = []
        for snapshot in capture["snapshots"]:
            native = (
                np.array(snapshot["environment_sugar"]).reshape(256, 256).T[::-1, :]
            )
            assert set(np.unique(native)) <= set(range(-1, 5))
            native = np.where(native == -1, 5, native)
            records.append(
                {
                    "native_iteration": snapshot["step"] + 1,
                    "matching_cell_classes": int(np.count_nonzero(author == native)),
                    "native_red_cells": int(np.count_nonzero(native == 5)),
                    "shared_red_coordinates": int(
                        np.count_nonzero((author == 5) & (native == 5))
                    ),
                }
            )
        best = max(r["matching_cell_classes"] for r in records)
        results.append(
            {
                "variant": variant,
                "image": name,
                "image_sha256": image_hash,
                "snapshots_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                "author_red_cells": int(np.count_nonzero(author == 5)),
                "best_matching_cell_classes": best,
                "best_native_iterations": [
                    r["native_iteration"]
                    for r in records
                    if r["matching_cell_classes"] == best
                ],
                "exact_native_iterations": [
                    r["native_iteration"]
                    for r in records
                    if r["matching_cell_classes"] == 65536
                ],
                "frames": records,
            }
        )
report = {
    "scope": "Post-hoc timing diagnostic across all recorded frames. No fitted crop, palette, orientation, or seed; best frame does not replace reported iteration.",
    "comparisons": 606,
    "results": results,
}
args.output.write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps([{k: v for k, v in r.items() if k != "frames"} for r in results]))
