"""Extract the predecessor's Figure14(a), run1, without assigning Figure3 parameters."""
import argparse
import csv
import hashlib
import json
from pathlib import Path

import fitz
import numpy as np

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("pdf", type=Path)
parser.add_argument("output", type=Path)
args = parser.parse_args()
source_hash = hashlib.sha256(args.pdf.read_bytes()).hexdigest()
assert source_hash == "2e375a0fb67a251b86f301920c075d7e43aaef4deb24ecf4e8df517535576053"
with fitz.open(args.pdf) as pdf:
    drawings = pdf[18].get_drawings()
assert len(drawings) == 1227
calibrations = {}
for name, indices, values, coordinate in [
    ("birth_cost", range(97, 102), np.arange(5) * 20, "x0"),
    ("gini", range(103, 107), np.array([.35, .40, .45, .50]), "y0"),
    ("mean_age", range(449, 456), np.arange(7) * 1000, "y0"),
]:
    positions = np.array([getattr(drawings[i]["rect"], coordinate) for i in indices])
    coefficients = np.polyfit(positions, values, 1)
    error = float(np.max(np.abs((values - coefficients[1]) / coefficients[0] - positions)))
    assert error < .01
    calibrations[name] = {"coefficients": coefficients.tolist(), "max_tick_error_pdf_points": error}
records = {}
x_errors = []
for metric, indices in [
    ("mean_age", list(range(400, 448)) + list(range(456, 504))),
    ("gini", list(range(0, 96, 2)) + list(range(107, 203, 2))),
]:
    records[metric] = {}
    for index in indices:
        drawing = drawings[index]
        if metric == "mean_age":
            assert [item[0] for item in drawing["items"]] == ["c"] * 4
        else:
            assert len(drawing["items"]) == len(drawings[index + 1]["items"]) == 1
            assert abs(drawing["rect"].height) < .001
            assert abs(drawings[index + 1]["rect"].width) < .001
        rect = drawing["rect"]
        x, y = (rect.x0 + rect.x1) / 2, (rect.y0 + rect.y1) / 2
        parameter = float(np.polyval(calibrations["birth_cost"]["coefficients"], x))
        cost = round(parameter)
        x_errors.append(abs(parameter - cost))
        assert abs(parameter - cost) < .005 and cost not in records[metric]
        records[metric][cost] = {"value": float(np.polyval(calibrations[metric]["coefficients"], y)), "drawing_index": index, "pdf_x": x, "pdf_y": y}
assert set(records["mean_age"]) == set(records["gini"]) == set(range(1, 97))
rows = [{"birth_cost": cost, "mean_age": records["mean_age"][cost]["value"], "gini": records["gini"][cost]["value"], "age_drawing_index": records["mean_age"][cost]["drawing_index"], "gini_drawing_index": records["gini"][cost]["drawing_index"]} for cost in range(1, 97)]
args.output.mkdir(parents=True, exist_ok=False)
with (args.output / "points.csv").open("w") as stream:
    writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
    writer.writeheader()
    writer.writerows(rows)
audit = {"source_sha256": source_hash, "pdf_page": 19, "figure": "14(a)", "run": 1, "points": len(rows), "birth_cost_values": list(range(1, 97)), "fixed_infertility": 10, "fixed_puberty": 1, "caption_window": [130000, 150000], "calibrations": calibrations, "maximum_birth_cost_integer_residual": max(x_errors), "cost40": rows[39], "points_sha256": hashlib.sha256((args.output / "points.csv").read_bytes()).hexdigest(), "scope": "Graphical targets from the predecessor's named run1, not raw author data. Seed and repetition aggregation unknown. This sweep is not assigned to target Figure3; no simulation agreement or completion inferred."}
(args.output / "audit.json").write_text(json.dumps(audit, indent=2) + "\n")
print(json.dumps({"points": len(rows), "cost40": rows[39], "maximum_parameter_residual": max(x_errors)}))
