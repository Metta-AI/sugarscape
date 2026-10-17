"""Freeze Figure 5b raster targets before fresh native population output exists."""

import argparse
import hashlib
import json
from pathlib import Path

import fitz
import numpy as np

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("paper", type=Path)
parser.add_argument("output", type=Path)
args = parser.parse_args()
paper = args.paper.resolve()
root = args.output.resolve()
root.mkdir(parents=True, exist_ok=False)
assert (
    hashlib.sha256(paper.read_bytes()).hexdigest()
    == "1cdff1a896e4c36e2247a726a9acb27a09ee491cecdc60cab17c4f85f9aa6916"
)
document = fitz.open(paper)
page = document[17]
assert page.get_images(full=True)[0][0] == 340
pixmap = fitz.Pixmap(document, 340)
assert (pixmap.width, pixmap.height, pixmap.n) == (1412, 830, 3)
pixmap.save(root / "figure5.png")
array = (
    np.frombuffer(pixmap.samples, dtype=np.uint8).reshape(830, 1412, 3).astype(float)
)
# Tick centers read from the original raster, checked against visible labels.
x_ticks = np.array([888, 988, 1087, 1187, 1287, 1386.5])
y_ticks = np.array([142, 223, 305, 386, 468, 549, 631])
x_fit = np.polyfit(np.arange(0, 51, 10), x_ticks, 1)
y_fit = np.polyfit(np.arange(500, 199, -50), y_ticks, 1)
# Blue line is separated from grey axes and black labels; no model output input.
trace = []
for x in range(888, 1378):
    column = array[125:645, x]
    weights = np.minimum(column[:, 2] - column[:, 0], column[:, 2] - column[:, 1])
    selected = weights > 30
    assert selected.any(), x
    y = float(np.average(np.arange(125, 645)[selected], weights=weights[selected]))
    trace.append([x, y, (x - x_fit[1]) / x_fit[0], (y - y_fit[1]) / y_fit[0]])
trace = np.array(trace)
np.savetxt(
    root / "pixel-trace.csv",
    trace,
    delimiter=",",
    header="pixel_x,pixel_y,time,population",
    comments="",
    fmt="%.9f",
)
targets = np.interp(np.arange(50), trace[:, 2], trace[:, 3])
np.savetxt(
    root / "population-target.csv",
    np.column_stack([np.arange(50), targets]),
    delimiter=",",
    header="time,population_digitized",
    comments="",
    fmt=["%d", "%.6f"],
)
record = {
    "scope": "Figure 5b raster digitization only; no fresh replication result.",
    "paper_sha256": hashlib.sha256(paper.read_bytes()).hexdigest(),
    "page_one_based": 18,
    "image_xref": 340,
    "x_tick_centers": x_ticks.tolist(),
    "x_tick_values": list(range(0, 51, 10)),
    "y_tick_centers": y_ticks.tolist(),
    "y_tick_values": list(range(500, 199, -50)),
    "x_pixel_fit": x_fit.tolist(),
    "y_pixel_fit": y_fit.tolist(),
    "acceptance_frozen_before_native_output": {
        "maximum_absolute_population_error": 2.0,
        "times": list(range(50)),
        "rationale": "Allows raster line width, antialiasing and subpixel axis calibration. Do not change after native output.",
    },
    "limitations": [
        "Raster curve is not author raw data.",
        "Figure seed is not stated in caption; released population exporter uses seed 42.",
        "Failure requires checking source revision, seed, time indexing and model semantics before any negative verdict.",
    ],
    "artifacts": {
        name: hashlib.sha256((root / name).read_bytes()).hexdigest()
        for name in ["figure5.png", "pixel-trace.csv", "population-target.csv"]
    },
}
(root / "target-protocol.json").write_text(json.dumps(record, indent=2) + "\n")
print(
    json.dumps(
        {"first_10": targets[:10].tolist(), "last": targets[-1], "points": len(targets)}
    )
)
