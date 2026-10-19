"""Compare Figure 5a raster occupancy with exported native states at times 49 and 50."""

import argparse
import csv
import hashlib
import json
from pathlib import Path

import fitz
import numpy as np

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("paper", type=Path)
parser.add_argument("native", type=Path)
parser.add_argument("output", type=Path)
args = parser.parse_args()
assert (
    hashlib.sha256(args.paper.read_bytes()).hexdigest()
    == "1cdff1a896e4c36e2247a726a9acb27a09ee491cecdc60cab17c4f85f9aa6916"
)
args.output.mkdir(parents=True, exist_ok=False)
document = fitz.open(args.paper)
pixmap = fitz.Pixmap(document, 340)
assert (pixmap.width, pixmap.height, pixmap.n) == (1412, 830, 3)
array = (
    np.frombuffer(pixmap.samples, dtype=np.uint8).reshape(830, 1412, 3)[:760, :780]
    / 255
)
blue = (array[:, :, 2] > 0.6) & (array[:, :, 0] < 0.4) & (array[:, :, 1] < 0.4)
counts = []
for x in range(50):
    for y in range(50):
        cx, cy = 6 + 15.2 * x, 6 + 15.2 * (49 - y)
        count = int(
            blue[
                max(0, round(cy - 7.6)) : round(cy + 7.6),
                max(0, round(cx - 7.6)) : round(cx + 7.6),
            ].sum()
        )
        counts.append((x, y, count))
expected = {(x, y) for x, y, count in counts if count > 60}
assert all(
    {(x, y) for x, y, count in counts if count > threshold} == expected
    for threshold in [25, 50, 80, 100]
)
np.savetxt(
    args.output / "grid-blue-counts.csv",
    counts,
    delimiter=",",
    fmt="%d",
    header="x,y,blue_pixels",
    comments="",
)
raw = (args.native / "popSize.csv").read_bytes()
assert (
    hashlib.sha256(raw).hexdigest()
    == "7041966cfe7bd056e64a49174535cc4ef793d4f5022abaf6f64e77b692b98704"
)
reports = []
for time in [49, 50]:
    with (args.native / f"agents-{time}.csv").open() as handle:
        agents = list(csv.DictReader(handle))
    with (args.native / f"cells-{time}.csv").open() as handle:
        cells = list(csv.DictReader(handle))
    actual = {(int(row["x"]), int(row["y"])) for row in agents}
    assert len(actual) == len(agents) == 206
    assert all(0 <= x < 50 and 0 <= y < 50 for x, y in actual)
    assert len({int(row["id"]) for row in agents}) == len(agents)
    assert {(int(row["x"]), int(row["y"])) for row in cells} == {
        (x, y) for x in range(50) for y in range(50)
    }
    assert len(cells) == 2500
    assert all(0 <= float(row["sugar"]) <= float(row["capacity"]) <= 4 for row in cells)
    occupied = {
        (int(row["x"]), int(row["y"])): int(row["occupier"])
        for row in cells
        if int(row["occupier"]) != -1
    }
    assert occupied == {
        (int(row["x"]), int(row["y"])): int(row["id"]) for row in agents
    }
    reports.append(
        {
            "time": time,
            "native_agents": len(agents),
            "published_occupied_cells": len(expected),
            "shared_coordinates": len(actual & expected),
            "native_only": sorted(actual - expected),
            "paper_only": sorted(expected - actual),
            "exact_match": actual == expected,
            "all_2500_cell_bounds_valid": True,
            "agent_occupancy_ids_exact": True,
        }
    )
report = {
    "observer_population_byteidentical": True,
    "population_sha256": hashlib.sha256(raw).hexdigest(),
    "comparisons": reports,
    "primary_time": 50,
    "diagnostic_time": 49,
    "scope": "Figure5a comparison for sequential seed42 only. Screenshot implementation/seed unspecified; no negative paper verdict.",
    "native_sha256": {
        name: hashlib.sha256((args.native / name).read_bytes()).hexdigest()
        for name in [
            "popSize.csv",
            "agents-49.csv",
            "agents-50.csv",
            "cells-49.csv",
            "cells-50.csv",
        ]
    },
}
(args.output / "audit.json").write_text(json.dumps(report, indent=2) + "\n")
print(
    json.dumps(
        {
            "published_occupied_cells": len(expected),
            "shared_coordinates": [row["shared_coordinates"] for row in reports],
        }
    )
)
