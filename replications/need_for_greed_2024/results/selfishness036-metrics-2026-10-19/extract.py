"""Extract the paper's vector population curves and compare the audited 0.36 cohort."""

from pathlib import Path
import hashlib
import json
import math
import sys

import fitz

paper, cohort_path, output = map(Path, sys.argv[1:])
assert not output.exists()
assert (
    hashlib.sha256(paper.read_bytes()).hexdigest()
    == "d96fbf4e514207590a4fd38636cf47199781876f956b2c1c6e21381c167c921c"
)
cohort_raw = cohort_path.read_bytes()
cohort = json.loads(cohort_raw)
assert cohort["native_inputs"] == 100 and cohort["condition"] == 0.36
page = fitz.open(paper)[4]
drawings = page.get_drawings()
axes = drawings[50]
assert axes["items"][0][0] == "re" and axes["color"] == (0, 0, 0)
box = axes["rect"]
assert (
    362 < box.x0 < 363
    and 545 < box.x1 < 546
    and 60 < box.y0 < 61
    and 165 < box.y1 < 166
)
words = page.get_text("words")
assert [w[4] for w in words if 330 < w[0] < 358 and 55 < w[1] < 170] == [
    "0",
    "200",
    "400",
    "600",
    "800",
    "1000",
    "1200",
    "1400",
]
assert [w[4] for w in words if 360 < w[0] < 550 and 172 < w[1] < 174] == [
    "0",
    "0.1",
    "0.2",
    "0.3",
    "0.4",
    "0.5",
    "0.6",
    "0.7",
    "0.8",
    "0.9",
    "1",
]
curves = {}
for name, index in [("median", 29), ("first_quartile", 32), ("third_quartile", 41)]:
    drawing = drawings[index]
    assert len(drawing["items"]) == 100
    assert drawing["color"] == ((1, 0, 1) if name == "median" else (0, 0, 0))
    points = [drawing["items"][0][1]]
    for item in drawing["items"]:
        assert item[0] == "l" and item[1] == points[-1]
        points.append(item[2])
    records = []
    for i, point in enumerate(points):
        factor = (point.x - box.x0) / box.width
        assert abs(factor - i / 100) < 0.00004
        population = (box.y1 - point.y) * 1400 / box.height
        records.append(
            {
                "selfishness": i / 100,
                "pdf_xy": list(point),
                "population_centerline": population,
            }
        )
    curves[name] = {
        "drawing_index": index,
        "stroke_width_points": drawing["width"],
        "dash_pattern": drawing["dashes"],
        "records": records,
    }
assert all(
    curves["first_quartile"]["records"][i]["population_centerline"]
    <= curves["median"]["records"][i]["population_centerline"]
    <= curves["third_quartile"]["records"][i]["population_centerline"]
    for i in range(101)
)
comparisons = []
for convention, value in cohort["population_medians"].items():
    x = box.x0 + 0.36 * box.width
    y = box.y1 - value * box.height / 1400
    distances = []
    records = curves["median"]["records"]
    for a, b in zip(records[:-1], records[1:]):
        ax, ay = a["pdf_xy"]
        bx, by = b["pdf_xy"]
        dx, dy = bx - ax, by - ay
        t = max(0, min(1, ((x - ax) * dx + (y - ay) * dy) / (dx * dx + dy * dy)))
        distances.append(math.hypot(x - ax - t * dx, y - ay - t * dy))
    distance = min(distances)
    comparisons.append(
        {
            "convention": convention,
            "replication_median": value,
            "pdf_xy": [x, y],
            "paper_centerline_at_vertex": records[36]["population_centerline"],
            "distance_to_median_path_points": distance,
            "half_stroke_width_points": curves["median"]["stroke_width_points"] / 2,
            "within_nominal_stroke": distance
            <= curves["median"]["stroke_width_points"] / 2,
        }
    )
report = {
    "paper_sha256": hashlib.sha256(paper.read_bytes()).hexdigest(),
    "pdf_page_zero_based": 4,
    "figure": 2,
    "pymupdf_version": fitz.VersionBind,
    "axes_pdf_rectangle": list(box),
    "axes_limits": {"selfishness": [0, 1], "population": [0, 1400]},
    "cohort_sha256": hashlib.sha256(cohort_raw).hexdigest(),
    "curves": curves,
    "comparisons": comparisons,
    "scope": "Direct PDF vector extraction with visually checked axes and caption. Stroke inclusion is graphical agreement under this axis calibration, not statistical equivalence or identification of historical time averaging. Dashed quartile centerlines retain gaps as dash metadata; no continuous ink is inferred. Only the audited 0.36 cohort is compared, not all 101 conditions.",
}
output.write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps(comparisons, indent=2))
