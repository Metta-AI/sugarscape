"""Extract published population median ink bounds, not statistical intervals."""

import argparse
import csv
import hashlib
import json
from pathlib import Path

import fitz

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("paper", type=Path)
parser.add_argument("output", type=Path)
parser.add_argument("--figure", type=int, choices=(10, 16), required=True)
args = parser.parse_args()
page, frame_index, curve_index, segments, selected, factor_name = {
    10: (14, 166, 167, 200, 37, "selfishness_hundredths"),
    16: (16, 29, 30, 210, 50, "utilitarian_percent"),
}[args.figure]
paper_sha = hashlib.sha256(args.paper.read_bytes()).hexdigest()
assert paper_sha == "56f25d6c9c3947954e29689a4fbd4c2ff0c09abd6515e631311939b747d4d51d"
with fitz.open(args.paper) as pdf:
    drawings = pdf[page].get_drawings()

# Visually checked axes: selfishness 0–1 or utilitarian 0–100%; population 0–1400.
# The frame and median are filled outlines, not stroked centerline paths.
frame = drawings[frame_index]["rect"]
curve = drawings[curve_index]
assert curve["fill"] == (1.0, 0.0, 1.0)
assert len(curve["items"]) == segments
assert all(item[0] == "l" for item in curve["items"])
frame_half_width = 0.143
x0, y0 = frame.x0 + frame_half_width, frame.y0 + frame_half_width
x1, y1 = frame.x1 - frame_half_width, frame.y1 - frame_half_width
rows = []
# Endpoints are deliberately excluded: the line caps need a separate treatment.
for hundredths in range(1, 100):
    x = x0 + (x1 - x0) * hundredths / 100
    intersections = []
    for _, start, end in curve["items"]:
        if min(start.x, end.x) <= x < max(start.x, end.x):
            intersections.append(
                start.y + (x - start.x) / (end.x - start.x) * (end.y - start.y)
            )
    assert len(intersections) == 2, (hundredths, intersections)
    low_y, high_y = sorted(intersections)
    rows.append(
        {
            factor_name: hundredths,
            "pdf_x": x,
            "ink_top_pdf_y": low_y,
            "ink_bottom_pdf_y": high_y,
            "population_ink_lower": (y1 - high_y) / (y1 - y0) * 1400,
            "population_ink_upper": (y1 - low_y) / (y1 - y0) * 1400,
        }
    )

args.output.mkdir(parents=True, exist_ok=False)
with (args.output / "median-ink-bounds.csv").open("w") as output:
    writer = csv.DictWriter(output, fieldnames=list(rows[0]))
    writer.writeheader()
    writer.writerows(rows)
report = {
    "paper_sha256": paper_sha,
    "pdf_page_one_based": page + 1,
    "figure": args.figure,
    "frame_drawing_index": frame_index,
    "median_drawing_index": curve_index,
    "axis_centers_pdf_points": [x0, y0, x1, y1],
    "frame_half_width_pdf_points": frame_half_width,
    "interior_factors": len(rows),
    "selected_factor": rows[selected - 1],
    "definition_from_caption": "Median of per-run mean population over 500 seeds.",
    "limits": [
        "Ink bounds are graphical precision bounds, not confidence or quartile intervals.",
        "PDF coordinate rounding and frame-center approximation remain additional uncertainty.",
        "Endpoint caps and dotted quartile curves are not extracted.",
        "Time averaging, extinction handling and historical quantile convention remain unresolved.",
        "No simulation comparison or replication verdict is made here.",
    ],
}
(args.output / "target.json").write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps(report, indent=2))
