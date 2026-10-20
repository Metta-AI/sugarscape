"""Compare Figure 3 markers with the preceding paper's Figure 16."""

import argparse
import csv
import hashlib
import json
from pathlib import Path

import fitz
import numpy as np

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("predecessor", type=Path)
parser.add_argument("output", type=Path)
args = parser.parse_args()
source_sha = hashlib.sha256(args.predecessor.read_bytes()).hexdigest()
assert source_sha == "2e375a0fb67a251b86f301920c075d7e43aaef4deb24ecf4e8df517535576053"
targets = Path(__file__).parent / "results/figure3-vector-targets-2026-10-19"
validation = json.loads((targets / "validation.json").read_text())
raw = (targets / "markers.csv").read_bytes()
assert hashlib.sha256(raw).hexdigest() == validation["files_sha256"]["markers.csv"]
rows = list(csv.DictReader(raw.decode().splitlines()))
with fitz.open(args.predecessor) as pdf:
    drawings = pdf[20].get_drawings()
assert len(drawings) == 542
comparisons = []
calibrations = []
for panel, age_ticks, value_ticks, values in [
    (
        "wealth",
        range(51, 56),
        range(57, 65),
        [500, 1000, 2000, 5000, 10000, 20000, 50000, 100000],
    ),
    ("gini", range(324, 329), range(330, 334), [0.4, 0.5, 0.6, 0.7]),
]:
    age_positions = np.array([drawings[i]["items"][0][1].x for i in age_ticks])
    value_positions = np.array([drawings[i]["items"][0][1].y for i in value_ticks])
    age_fit = np.polyfit(age_positions, range(5), 1)
    value_fit = np.polyfit(value_positions, np.log10(values), 1)
    for name, positions, logs, coefficients in [
        ("age", age_positions, np.arange(5), age_fit),
        ("value", value_positions, np.log10(values), value_fit),
    ]:
        error = float(
            np.max(np.abs((logs - coefficients[1]) / coefficients[0] - positions))
        )
        assert error < 0.005, (panel, name, error)
        calibrations.append(
            {
                "panel": panel,
                "axis": name,
                "coefficients": coefficients.tolist(),
                "max_tick_error_pdf_points": error,
            }
        )
    for row in rows:
        if row["panel"] != panel:
            continue
        index = int(row["drawing_index"]) + (1 if panel == "gini" else 0)
        rect = drawings[index]["rect"]
        x, y = (rect.x0 + rect.x1) / 2, (rect.y0 + rect.y1) / 2
        old_age = float(10 ** np.polyval(age_fit, x))
        old_value = float(10 ** np.polyval(value_fit, y))
        age, value = float(row["mean_age"]), float(row["value"])
        comparisons.append(
            {
                "panel": panel,
                "family": row["parameter_family"],
                "ordinal": int(row["marker_ordinal"]),
                "predecessor_drawing_index": index,
                "target_age": age,
                "predecessor_age": old_age,
                "target_value": value,
                "predecessor_value": old_value,
                "relative_age_difference": abs(old_age - age) / age,
                "relative_value_difference": abs(old_value - value) / value,
            }
        )
assert len(comparisons) == 362
args.output.mkdir(parents=True, exist_ok=False)
with (args.output / "comparisons.csv").open("w") as output:
    writer = csv.DictWriter(output, fieldnames=list(comparisons[0]))
    writer.writeheader()
    writer.writerows(comparisons)
report = {
    "predecessor_sha256": source_sha,
    "target_markers_sha256": hashlib.sha256(raw).hexdigest(),
    "predecessor_pdf_page": 21,
    "markers_compared": len(comparisons),
    "max_relative_age_difference": max(
        r["relative_age_difference"] for r in comparisons
    ),
    "max_relative_value_difference": max(
        r["relative_value_difference"] for r in comparisons
    ),
    "calibrations": calibrations,
    "scope": "Graphic-coordinate comparison supports reuse of the plotted data. It does not recover raw observations, numerical parameter assignments, seeds or the target-paper averaging protocol.",
}
(args.output / "audit.json").write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps(report, indent=2))
