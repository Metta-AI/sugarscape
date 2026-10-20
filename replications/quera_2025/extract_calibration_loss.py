"""Extract displayed loss vertices; compare two independent PDF renderers.

Usage: python extract_calibration_loss.py PAPER_FIGURE.pdf POPPLER.svg NEW_OUTPUT
The SVG must be made by pdftocairo -svg from the same PDF.
"""

import argparse
import bisect
import math
import csv
import hashlib
import json
import re
import statistics
import xml.etree.ElementTree as ET
from pathlib import Path

import fitz

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("pdf", type=Path)
parser.add_argument("svg", type=Path)
parser.add_argument("output", type=Path)
args = parser.parse_args()
page = fitz.open(args.pdf)[0]
text = page.get_text()
assert "Pathwise (best: -175.0)" in text
assert "Score (best: -172.0)" in text
paths = page.get_drawings()
# The second PDF rectangle is the axes background; tick labels are retained below.
box = paths[1]["items"][0][1]
xticks = []
yticks = []
for path in paths:
    if len(path["items"]) != 1 or path["items"][0][0] != "l":
        continue
    _, start, end = path["items"][0]
    if start.y == box.y1 and start.x == end.x and abs(start.y - end.y - 3) < 1e-5:
        xticks.append(start.x)
    if start.x == box.x0 and start.y == end.y and abs(end.x - start.x - 3) < 1e-5:
        yticks.append(start.y)
assert len(xticks) == 4 and len(yticks) == 2
xticks.sort()
yticks.sort()
xs, xi = statistics.linear_regression(xticks, [0, 1000, 2000, 3000])
ys, yi = statistics.linear_regression(yticks, [0, -100])
curves = [p for p in paths if len(p["items"]) > 100]
svg_curves = [
    e
    for e in ET.parse(args.svg).getroot().iter()
    if e.tag.endswith("path") and len(e.attrib.get("d", "")) > 20000
]
assert len(curves) == len(svg_curves) == 4
rows = []
summaries = []
for index, (curve, svg) in enumerate(zip(curves, svg_curves)):
    assert all(item[0] == "l" for item in curve["items"])
    points = [curve["items"][0][1]] + [item[2] for item in curve["items"]]
    assert all(a[2] == b[1] for a, b in zip(curve["items"], curve["items"][1:]))
    values = [
        float(v)
        for v in re.findall(r"[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?", svg.attrib["d"])
    ]
    # Cairo may omit collinear vertices. Compare both polylines geometrically,
    # rather than requiring their vertex arrays to be identical.
    native = [(p.x, page.rect.height - p.y) for p in points]
    converted = list(zip(values[::2], values[1::2]))
    coordinate_error = 0.0
    for source, target in [(native, converted), (converted, native)]:
        target_x = [p[0] for p in target]
        for x, y in source:
            nearest = bisect.bisect_left(target_x, x)
            distances = []
            for segment in range(
                max(0, nearest - 2), min(len(target) - 1, nearest + 2)
            ):
                ax, ay = target[segment]
                bx, by = target[segment + 1]
                dx, dy = bx - ax, by - ay
                fraction = max(
                    0, min(1, ((x - ax) * dx + (y - ay) * dy) / (dx * dx + dy * dy))
                )
                distances.append(
                    math.hypot(x - ax - fraction * dx, y - ay - fraction * dy)
                )
            coordinate_error = max(coordinate_error, min(distances))
    # 1/256-point Cairo coordinate quantization in two dimensions, plus float error.
    assert coordinate_error < 0.006
    iterations = [xs * p.x + xi for p in points]
    integer_error = max(abs(t - round(t)) for t in iterations)
    assert integer_error < 0.001
    assert round(iterations[0]) == 0 and round(iterations[-1]) == 2999
    assert all(a < b for a, b in zip(iterations, iterations[1:]))
    method = ["pathwise", "score"][index % 2]
    opacity = curve["stroke_opacity"]
    assert opacity == float(svg.attrib["stroke-opacity"])
    for point, iteration in zip(points, iterations):
        rows.append(
            [method, opacity, round(iteration), ys * point.y + yi, point.x, point.y]
        )
    summaries.append(
        {
            "method": method,
            "opacity": opacity,
            "vertices": len(points),
            "svg_vertices": len(converted),
            "first_iteration": 0,
            "last_iteration": 2999,
            "maximum_cross_renderer_coordinate_error_points": coordinate_error,
            "maximum_integer_iteration_error": integer_error,
        }
    )
args.output.mkdir(exist_ok=False)
with (args.output / "loss-vertices.csv").open("w") as stream:
    writer = csv.writer(stream)
    writer.writerow(
        ["method", "opacity", "iteration", "displayed_loss", "pdf_x", "pdf_y"]
    )
    writer.writerows(rows)
(args.output / "figure-text.txt").write_text(text)
(args.output / "audit.json").write_text(
    json.dumps(
        {
            "pdf_sha256": hashlib.sha256(args.pdf.read_bytes()).hexdigest(),
            "svg_sha256": hashlib.sha256(args.svg.read_bytes()).hexdigest(),
            "extractor_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            "pymupdf_version": fitz.VersionBind,
            "x_tick_values": [0, 1000, 2000, 3000],
            "x_tick_positions": xticks,
            "y_tick_values": [0, -100],
            "y_tick_positions": yticks,
            "curves": summaries,
            "vertices": len(rows),
            "scope": "Displayed simplified PDF vertices, not raw training records. Opacity distinguishes the four curves; smoothing and training/validation roles are unknown. All displayed paths span iterations0–2999. The appendix specifies5000 epochs; neither missing epochs nor early stopping are established by this figure.",
        },
        indent=2,
    )
    + "\n"
)
print(json.dumps(summaries))
