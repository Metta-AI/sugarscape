"""Recover the six finite-difference polylines from the original figure's SVG conversion."""

import argparse
import csv
import hashlib
import json
import re
import statistics
import xml.etree.ElementTree as E
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument("svg", type=Path)
parser.add_argument("output", type=Path)
args = parser.parse_args()
paths = []
for element in E.parse(args.svg).getroot().iter():
    if element.tag.endswith("path") and "stroke" in element.attrib:
        values = [
            float(v)
            for v in re.findall(
                r"[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?", element.attrib.get("d", "")
            )
        ]
        paths.append((element.attrib, values))
vertical = sorted(
    {
        v[0]
        for p, v in paths
        if len(v) == 4 and v[0] == v[2] and abs(v[3] - v[1] - 83.160993) < 1e-4
    }
)
assert len(vertical) == 12
curves = [
    (p, v)
    for p, v in paths
    if p["stroke"] == "rgb(4.705811%, 36.470032%, 64.704895%)" and len(v) > 40
]
assert len(curves) == 6 and all(len(v) == 50 for p, v in curves)
# Tick values were read visually from the original PDF, including scientific multipliers.
names = [
    "vision_1",
    "vision_3",
    "metabolism_alpha",
    "metabolism_beta",
    "wealth_alpha",
    "wealth_beta",
]
yvalues = [
    [-0.05, 0],
    [0, 0.005, 0.01],
    [-0.15, -0.1, -0.05, 0],
    [0, 0.01, 0.02, 0.03],
    [0.005, 0.01, 0.015],
    [-0.02, -0.015, -0.01],
]
rows = []
panels = []
for panel, ((path, coordinates), name, values) in enumerate(
    zip(curves, names, yvalues)
):
    left, right = vertical[panel * 2 : panel * 2 + 2]
    yticks = sorted(
        v[1]
        for p, v in paths
        if len(v) == 4
        and abs(v[0] - left) < 1e-5
        and v[1] == v[3]
        and abs(v[2] - v[0] - 3) < 0.01
    )
    xticks = sorted(
        v[0]
        for p, v in paths
        if len(v) == 4
        and v[0] == v[2]
        and abs(v[1] - 28.811426) < 1e-5
        and left < v[0] < right
        and abs(v[3] - v[1] - 3) < 0.01
    )
    assert len(yticks) == len(values) and len(xticks) == 6
    yslope, yintercept = statistics.linear_regression(yticks, values)
    xslope, xintercept = statistics.linear_regression(xticks, [0, 5, 10, 15, 20, 25])
    tick_residual = max(
        abs(yslope * y + yintercept - value) for y, value in zip(yticks, values)
    )
    times = [xslope * x + xintercept for x in coordinates[::2]]
    assert max(abs(t - i) for t, i in zip(times, range(1, 26))) < 0.002
    for t, y in zip(times, coordinates[1::2]):
        rows.append(
            {"parameter": name, "time": round(t), "gradient": yslope * y + yintercept}
        )
    panels.append(
        {
            "parameter": name,
            "ticks": values,
            "tick_positions": yticks,
            "maximum_tick_fit_residual": tick_residual,
            "x_tick_positions": xticks,
            "source_path": path,
        }
    )
args.output.mkdir(exist_ok=False)
with (args.output / "finite-difference-curves.csv").open("w") as stream:
    writer = csv.DictWriter(stream, fieldnames=["parameter", "time", "gradient"])
    writer.writeheader()
    writer.writerows(rows)
(args.output / "audit.json").write_text(
    json.dumps(
        {
            "points": len(rows),
            "panels": panels,
            "svg_sha256": hashlib.sha256(args.svg.read_bytes()).hexdigest(),
            "scope": "Published plotted finite-difference coordinates, subject to PDF path rounding. No recovered raw simulations, Monte Carlo counts, step sizes, or automatic-differentiation samples.",
        },
        indent=2,
    )
    + "\n"
)
print(json.dumps({"points": len(rows), "initial_points": rows[::25]}))
