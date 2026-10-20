"""Audit all extracted host cells and independently reconstruct the sugar landscape."""

import argparse
from collections import Counter
import csv
import hashlib
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("states", type=Path)
parser.add_argument("hotspots", type=Path)
parser.add_argument("output", type=Path)
args = parser.parse_args()
with args.states.open() as stream:
    rows = [{k: int(v) for k, v in r.items()} for r in csv.DictReader(stream)]
assert len(rows) == 256 * 256
assert [(r["x"], r["y"]) for r in rows] == [
    (x, y) for x in range(256) for y in range(256)
]
assert all(r["step"] == -1 and r["status"] in [0, 1] for r in rows)
active = [r for r in rows if r["status"] == 1]
assert [r["id"] for r in active] == list(range(len(active)))
assert all(5 <= r["sugar"] <= 25 and 1 <= r["metabolism"] <= 4 for r in active)
assert all(
    r["id"] == -1 and r["sugar"] == r["metabolism"] == 0
    for r in rows
    if r["status"] == 0
)
assert all(0 <= r["cell_sugar"] == r["cell_capacity"] <= 4 for r in rows)
hotspots = []
for line in args.hotspots.read_text().splitlines():
    kind, x, y = line.split(",")
    assert kind == "HOTSPOT"
    hotspots.append((int(x), int(y)))
assert len(hotspots) == (2 * 256 * 256) // (49 * 49) == 54
assert all(0 <= x < 256 and 0 <= y < 256 for x, y in hotspots)
distances = []
for i, (x, y) in enumerate(hotspots):
    for xx, yy in hotspots[:i]:
        dx, dy = abs(x - xx), abs(y - yy)
        dx, dy = min(dx, 256 - dx), min(dy, 256 - dy)
        distances.append(float(np.sqrt(dx * dx + dy * dy)))
assert min(distances) >= 20
x, y = np.indices((256, 256))
capacity = np.zeros((256, 256), dtype=np.int64)
for hx, hy in hotspots:
    # Source casts Euclidean distance to float before dividing into radius-five bands.
    distance = np.sqrt(
        (hx - x).astype(np.float64) ** 2 + (hy - y).astype(np.float64) ** 2
    ).astype(np.float32)
    capacity += 4 - np.minimum(4, np.floor(distance / np.float32(5)).astype(np.int64))
capacity = np.minimum(4, capacity)
native = np.array([r["cell_capacity"] for r in rows]).reshape((256, 256))
assert np.array_equal(native, capacity)
args.output.mkdir(exist_ok=False)
report = {
    "states_sha256": hashlib.sha256(args.states.read_bytes()).hexdigest(),
    "hotspots_sha256": hashlib.sha256(args.hotspots.read_bytes()).hexdigest(),
    "cells": len(rows),
    "occupied_cells": len(active),
    "hotspots": len(hotspots),
    "minimum_wrapped_hotspot_separation": min(distances),
    "capacity_counts": dict(sorted(Counter(int(v) for v in native.flat).items())),
    "independent_exact_capacity_matches": int(np.count_nonzero(native == capacity)),
    "native_parity": "Pending GPU initial-state capture. This is extracted host initialization, not a full simulation or validated historical Figure11D match.",
    "numeric_rule": "Wrapped hotspot spacing, unwrapped Euclidean cell distances, float distance/radius arithmetic, summed bands clipped at4; unchanged source behavior.",
}
(args.output / "audit.json").write_text(json.dumps(report, indent=2) + "\n")
fig, ax = plt.subplots(figsize=(6.5, 6))
im = ax.imshow(
    native.T,
    origin="lower",
    cmap=plt.get_cmap("viridis", 5),
    vmin=-0.5,
    vmax=4.5,
    interpolation="nearest",
    extent=(-0.5, 255.5, -0.5, 255.5),
)
fig.colorbar(im, ax=ax, ticks=range(5), label="Initial sugar capacity")
ax.set(
    xlabel="x",
    ylabel="y",
    title="Extracted host initialization: seed 0, width 256\nGPU parity remains unverified",
)
fig.tight_layout()
fig.savefig(args.output / "landscape.png", dpi=160)
fig.savefig(args.output / "landscape.pdf")
plt.close(fig)
print(json.dumps(report))
