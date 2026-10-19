"""Recover Figure 3 marker centers without inventing parameter assignments."""

import argparse
import csv
import hashlib
import json
from pathlib import Path

import fitz
import numpy as np

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("figure", type=Path)
parser.add_argument("output", type=Path)
args = parser.parse_args()
digest = hashlib.sha256(args.figure.read_bytes()).hexdigest()
assert digest == "ce02d28efdcb43356b9925fb215c27500b740adf6c97c043b47bb8d0598207fb"
with fitz.open(args.figure) as pdf:
    drawings = pdf[0].get_drawings()
assert len(drawings) == 540

# The unrotated PDF stores plotted horizontal coordinates in page y.
# Tick labels and marker styles were checked against the upright source figure.
axes = [
    ("wealth_age", range(51, 56), [1, 10, 100, 1000, 10000], 1),
    ("gini_age", range(323, 328), [1, 10, 100, 1000, 10000], 1),
    ("wealth", range(57, 65), [500, 1000, 2000, 5000, 10000, 20000, 50000, 100000], 0),
    ("gini", range(329, 333), [0.4, 0.5, 0.6, 0.7], 0),
]
calibrations = {}
for name, indices, labels, coordinate in axes:
    positions = np.array([drawings[i]["items"][0][1][coordinate] for i in indices])
    coefficients = np.polyfit(positions, np.log10(labels), 1)
    reconstructed = (np.log10(labels) - coefficients[1]) / coefficients[0]
    error = float(np.max(np.abs(reconstructed - positions)))
    assert error < 0.005, (name, error)
    calibrations[name] = {
        "scale": "log10",
        "coefficients": coefficients.tolist(),
        "tick_positions": positions.tolist(),
        "tick_values": labels,
        "max_tick_error_pdf_points": error,
    }

rows = []
for panel, groups in [
    (
        "wealth",
        [
            ("puberty", range(0, 50)),
            ("infertility", range(65, 130)),
            ("birth_cost", range(130, 262, 2)),
        ],
    ),
    (
        "gini",
        [
            ("puberty", range(272, 322)),
            ("infertility", range(333, 398)),
            ("birth_cost", range(398, 530, 2)),
        ],
    ),
]:
    for parameter, indices in groups:
        for ordinal, index in enumerate(indices):
            drawing = drawings[index]
            rect = drawing["rect"]
            expected_size = 3.6 if parameter == "puberty" else 5.4
            assert abs(rect.width - expected_size) < 0.001
            assert abs(rect.height - expected_size) < 0.001
            assert drawing["color"] == (0.0, 0.0, 0.0)
            if parameter == "birth_cost":
                assert len(drawing["items"]) == 1
                assert all(
                    abs(a - b) < 0.001
                    for a, b in zip(rect, drawings[index + 1]["rect"], strict=True)
                )
            else:
                assert len(drawing["items"]) == 4
                assert (drawing["fill"] == (0.0, 0.0, 0.0)) == (parameter == "puberty")
            x = (rect.x0 + rect.x1) / 2
            y = (rect.y0 + rect.y1) / 2
            rows.append(
                {
                    "panel": panel,
                    "parameter_family": parameter,
                    "marker_ordinal": ordinal,
                    "drawing_index": index,
                    "pdf_x": x,
                    "pdf_y": y,
                    "mean_age": float(
                        10
                        ** np.polyval(calibrations[f"{panel}_age"]["coefficients"], y)
                    ),
                    "value": float(
                        10 ** np.polyval(calibrations[panel]["coefficients"], x)
                    ),
                }
            )
assert len(rows) == 362
args.output.mkdir(parents=True, exist_ok=False)
with (args.output / "markers.csv").open("w") as output:
    writer = csv.DictWriter(output, fieldnames=list(rows[0]))
    writer.writeheader()
    writer.writerows(rows)
report = {
    "source_sha256": digest,
    "markers": len(rows),
    "per_panel": {"puberty": 50, "infertility": 65, "birth_cost": 66},
    "calibrations": calibrations,
    "limitations": [
        "Marker centers are rounded graphic coordinates, not recovered raw simulation observations.",
        "The figure labels parameter families but does not assign numeric parameter values to individual markers.",
        "Panel marker ordinals are retained separately and are not asserted to identify paired simulation runs.",
        "Original seeds, repetitions and steady-state averaging windows remain unidentified.",
        "This extraction does not establish simulation agreement or paper completion.",
    ],
}
(args.output / "audit.json").write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps({"markers": len(rows), "per_panel": report["per_panel"]}))
