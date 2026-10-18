"""Extract Sugarscape curve vertices from the pinned accepted-manuscript PDF."""

import argparse
import hashlib
import itertools
import json
import math
from pathlib import Path

import fitz

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("pdf", type=Path)
parser.add_argument("output", type=Path)
args = parser.parse_args()
expected = json.loads(
    (Path(__file__).parent / "paper-targets/targets.json").read_text()
)
assert hashlib.sha256(args.pdf.read_bytes()).hexdigest() == expected["paper_sha256"]
page = fitz.open(args.pdf)[17]
drawings = page.get_drawings()
x1000 = drawings[163]["items"][0][1].x
x1000000 = drawings[163]["items"][3][1].x
y001 = drawings[165]["items"][0][1].y
y100 = drawings[165]["items"][4][1].y
rows = []
for backend, drawing, count in [
    ("mason", 167, 11),
    ("flamegpu", 168, 13),
    ("flame", 169, 5),
    ("c", 170, 7),
]:
    lines = drawings[drawing]["items"]
    assert all(line[0] == "l" for line in lines)
    points = [lines[0][1], *[line[2] for line in lines]]
    assert len(points) == count
    for point in points:
        requested = 10 ** (3 + 3 * (point.x - x1000) / (x1000000 - x1000))
        nominal = 250 * 2 ** round(math.log2(requested / 250))
        assert abs(requested / nominal - 1) < 0.0003
        runtime = 10 ** (2 - 4 * (point.y - y100) / (y001 - y100))
        perturbed = [
            10 ** (2 - 4 * (point.y + dy - y100 - dh) / (y001 + dl - y100 - dh))
            for dy, dl, dh in itertools.product([-0.001, 0.001], repeat=3)
        ]
        rows.append(
            {
                "backend": backend,
                "requested_cells": nominal,
                "digitized_requested_cells": requested,
                "runtime_seconds": runtime,
                "pdf_point": [point.x, point.y],
                "drawing_index": drawing,
                "coordinate_sensitivity_seconds": [min(perturbed), max(perturbed)],
            }
        )
args.output.write_text(
    json.dumps(
        {
            "paper_sha256": expected["paper_sha256"],
            "figure": 4,
            "pdf_page_index": 17,
            "curve_identity": "Visually matched legend markers: MASON triangle, FLAME GPU open circle, FLAME filled circle, C square.",
            "calibration": {
                "x1000": x1000,
                "x1000000": x1000000,
                "y001": y001,
                "y100": y100,
            },
            "points": rows,
            "uncertainty": "Coordinate sensitivity independently perturbs vertex y and both y-axis calibration ticks by0.001 PDF points. This is not statistical uncertainty, recovered raw timing precision, or an acceptance margin.",
            "script_discrepancies": [
                "MASON includes256000 cells, beyond released128000 default maximum.",
                "C starts at500 cells; the released default starts at250.",
            ],
            "completed_study": False,
        },
        indent=2,
    )
    + "\n"
)
print(f"Extracted {len(rows)} curve points")
