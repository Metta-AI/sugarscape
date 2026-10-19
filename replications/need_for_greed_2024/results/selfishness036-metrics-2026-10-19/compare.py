"""Compare four additional median measurements with original PDF vector paths."""

from pathlib import Path
import hashlib
import json
import math
import sys

import fitz

paper, metrics_path, output = map(Path, sys.argv[1:])
assert not output.exists()
assert (
    hashlib.sha256(paper.read_bytes()).hexdigest()
    == "d96fbf4e514207590a4fd38636cf47199781876f956b2c1c6e21381c167c921c"
)
metrics_raw = metrics_path.read_bytes()
metrics = json.loads(metrics_raw)
assert metrics["inputs"] == 100 and metrics["observations"] == 490477
document = fitz.open(paper)
reports = []
for figure, page_index, axis_index, curve_index, low, high, metric in [
    (3, 4, 92, 71, 0, 350, "meanWealth"),
    (4, 5, 44, 23, 10, 20, "agentMeanTimeToLive"),
    (5, 5, 85, 64, 0, 30, "death_percent"),
    (6, 5, 127, 106, 0, 70, "meanAgeAtDeath"),
]:
    drawings = document[page_index].get_drawings()
    axes = drawings[axis_index]
    assert len(axes["items"]) == 1 and axes["items"][0][0] == "re"
    box = axes["rect"]
    curve = drawings[curve_index]
    assert curve["color"] == (1, 0, 1) and curve["dashes"] == "[] 0"
    assert len(curve["items"]) == 100
    points = [curve["items"][0][1]]
    for item in curve["items"]:
        assert item[0] == "l" and item[1] == points[-1]
        points.append(item[2])
    vertices = []
    for i, point in enumerate(points):
        assert abs((point.x - box.x0) / box.width - i / 100) < 0.00004
        vertices.append(
            {
                "selfishness": i / 100,
                "pdf_xy": list(point),
                "value": low + (box.y1 - point.y) * (high - low) / box.height,
            }
        )
    comparisons = []
    for name, value in metrics["medians"].items():
        if name.split("/")[0] != metric:
            continue
        x = box.x0 + 0.36 * box.width
        y = box.y1 - (value - low) * box.height / (high - low)
        distances = []
        for a, b in zip(points[:-1], points[1:]):
            dx, dy = b.x - a.x, b.y - a.y
            t = max(0, min(1, ((x - a.x) * dx + (y - a.y) * dy) / (dx * dx + dy * dy)))
            distances.append(math.hypot(x - a.x - t * dx, y - a.y - t * dy))
        distance = min(distances)
        comparisons.append(
            {
                "convention": name,
                "replication_median": value,
                "pdf_xy": [x, y],
                "distance_to_path_points": distance,
                "within_nominal_stroke": distance <= curve["width"] / 2,
            }
        )
    reports.append(
        {
            "figure": figure,
            "metric": metric,
            "pdf_page_zero_based": page_index,
            "axis_drawing_index": axis_index,
            "curve_drawing_index": curve_index,
            "axis_rectangle": list(box),
            "y_limits": [low, high],
            "stroke_width_points": curve["width"],
            "paper_centerline_at_036": vertices[36]["value"],
            "paper_vertices": vertices,
            "comparisons": comparisons,
        }
    )
report = {
    "paper_sha256": hashlib.sha256(paper.read_bytes()).hexdigest(),
    "metrics_sha256": hashlib.sha256(metrics_raw).hexdigest(),
    "pymupdf_version": fitz.VersionBind,
    "figures": reports,
    "scope": "Original vector curves with visually checked captions and axis limits. One complete 100-seed condition compared under explicit averaging conventions. Stroke inclusion is graphical agreement, not statistical equivalence; disagreement remains subject to measurement/source investigation.",
}
output.write_text(json.dumps(report, indent=2) + "\n")
print(
    json.dumps(
        [
            {
                k: f[k]
                for k in ["figure", "metric", "paper_centerline_at_036", "comparisons"]
            }
            for f in reports
        ],
        indent=2,
    )
)
