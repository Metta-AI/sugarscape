"""Audit recovered original Figure 5a pixels against repeated native state exports."""

import argparse
import csv
import hashlib
import json
from pathlib import Path

import fitz
import numpy as np

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("image", type=Path)
parser.add_argument("native", type=Path)
parser.add_argument("repeat", type=Path)
parser.add_argument("pdf_grid", type=Path)
parser.add_argument("output", type=Path)
args = parser.parse_args()
args.output.mkdir(parents=True)
pixmap = fitz.Pixmap(args.image)
assert (pixmap.width, pixmap.height, pixmap.n) == (797, 802, 4)
pixels = np.frombuffer(pixmap.samples, dtype=np.uint8).reshape(802, 797, 4)
blue = (pixels[:, :, 2] > 153) & (pixels[:, :, 0] < 102) & (pixels[:, :, 1] < 102)
yellow = (pixels[:, :, 0] > 150) & (pixels[:, :, 1] > 150) & (pixels[:, :, 2] < 100)
counts = []
for x in range(50):
    for y in range(50):
        region = np.s_[16 * (49 - y) : 16 * (50 - y), 16 * x : 16 * (x + 1)]
        counts.append((x, y, int(blue[region].sum()), int(yellow[region].sum())))
expected = {(x, y) for x, y, blue_count, _ in counts if blue_count > 60}
assert len(expected) == 201
for threshold in [25, 50, 80, 100]:
    assert {(x, y) for x, y, value, _ in counts if value > threshold} == expected
with args.pdf_grid.open() as handle:
    pdf = {
        (int(r["x"]), int(r["y"]))
        for r in csv.DictReader(handle)
        if int(r["blue_pixels"]) > 60
    }
assert pdf == expected
reports = []
files = []
for time in range(101):
    for name in [f"agents-{time}.csv", f"cells-{time}.csv"]:
        raw = (args.native / name).read_bytes()
        assert raw == (args.repeat / name).read_bytes()
        files.append({"name": name, "sha256": hashlib.sha256(raw).hexdigest()})
    with (args.native / f"agents-{time}.csv").open() as handle:
        agents = list(csv.DictReader(handle))
    with (args.native / f"cells-{time}.csv").open() as handle:
        cells = list(csv.DictReader(handle))
    actual = {(int(a["x"]), int(a["y"])): int(a["id"]) for a in agents}
    assert len(actual) == len(agents) == len({a["id"] for a in agents})
    assert len(cells) == 2500
    assert {(int(c["x"]), int(c["y"])) for c in cells} == {
        (x, y) for x in range(50) for y in range(50)
    }
    assert all(0 <= float(c["sugar"]) <= float(c["capacity"]) <= 4 for c in cells)
    assert {
        (int(c["x"]), int(c["y"])): int(c["occupier"])
        for c in cells
        if int(c["occupier"]) != -1
    } == actual
    reports.append(
        {
            "time": time,
            "population": len(agents),
            "shared_positions": len(expected & set(actual)),
            "mismatched_positions": len(expected ^ set(actual)),
        }
    )
assert [r["time"] for r in reports if r["mismatched_positions"] == 0] == [83]
with (args.native / "cells-83.csv").open() as handle:
    visible = {
        (int(c["x"]), int(c["y"])): int(float(c["sugar"]))
        for c in csv.DictReader(handle)
        if int(c["occupier"]) == -1
    }
# Exploratory raster characterization, not a preregistered renderer tolerance.
levels = []
for sugar in range(4):
    values = [
        yellow_count
        for x, y, _, yellow_count in counts
        if (x, y) in visible and visible[x, y] == sugar
    ]
    assert len(set(values)) == 1
    levels.append(
        {"native_sugar": sugar, "yellow_pixels": values[0], "cells": len(values)}
    )
assert sum(r["cells"] for r in levels) == 2299
assert [r["yellow_pixels"] for r in levels] == sorted(
    r["yellow_pixels"] for r in levels
)
raw = (args.native / "popSize.csv").read_bytes()
assert raw == (args.repeat / "popSize.csv").read_bytes()
files.append({"name": "popSize.csv", "sha256": hashlib.sha256(raw).hexdigest()})
result = {
    "image_sha256": hashlib.sha256(args.image.read_bytes()).hexdigest(),
    "occupied_cells": 201,
    "source_pdf_occupancy_exact": True,
    "exact_match_time": 83,
    "scanned_times": [0, 100],
    "state_observations": 252500,
    "byte_identical_files": len(files),
    "visible_resource_characterization": levels,
    "states": reports,
    "files": files,
    "scope": "Exact occupancy match at exported time83, not caption time50. Exploratory visible-resource characterization. Native GHC8.4.3; source-image historical compiler and capture time remain unrecorded. No timing-performance verdict.",
}
(args.output / "audit.json").write_text(json.dumps(result, indent=2) + "\n")
np.savetxt(
    args.output / "source-grid-pixels.csv",
    counts,
    delimiter=",",
    fmt="%d",
    header="x,y,blue_pixels,yellow_pixels",
    comments="",
)
print(
    json.dumps(
        {
            k: result[k]
            for k in [
                "exact_match_time",
                "occupied_cells",
                "byte_identical_files",
                "visible_resource_characterization",
            ]
        }
    )
)
