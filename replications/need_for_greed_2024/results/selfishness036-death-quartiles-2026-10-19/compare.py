"""Compare complete Figure5 curves against primary and diagnostic death definitions."""

import hashlib
import json
from pathlib import Path
import sys

import fitz
import numpy as np

workspace, fresh_metrics, output = map(Path, sys.argv[1:])
assert not output.exists()
study = workspace / "sugarscape-need-for-greed/replications/need_for_greed_2024/results"
raw = fresh_metrics.read_bytes()
assert (
    raw
    == (study / "selfishness036-metrics-2026-10-19/numpy-validation.json").read_bytes()
)
metrics = json.loads(raw)
assert metrics["native_runs"] == 100 and metrics["primary_values_checked"] == 2400
paper = (
    workspace / "sugarscape-replication-evidence/papers/need-for-greed-author-2024.pdf"
)
assert (
    hashlib.sha256(paper.read_bytes()).hexdigest()
    == "d96fbf4e514207590a4fd38636cf47199781876f956b2c1c6e21381c167c921c"
)
drawings = fitz.open(paper)[5].get_drawings()
box = drawings[85]["rect"]
curves = {}
for name, index in [("first_quartile", 67), ("median", 64), ("third_quartile", 76)]:
    drawing = drawings[index]
    assert drawing["color"] == ((1, 0, 1) if name == "median" else (0, 0, 0))
    points = [drawing["items"][0][1]]
    for item in drawing["items"]:
        assert item[0] == "l" and item[1] == points[-1]
        points.append(item[2])
    assert len(points) == (100 if name == "third_quartile" else 101)
    records = [
        {
            "selfishness": (p.x - box.x0) / box.width,
            "pdf_xy": list(p),
            "value": (box.y1 - p.y) * 30 / box.height,
        }
        for p in points
    ]
    target = [row for row in records if abs(row["selfishness"] - 0.36) < 0.00004]
    assert len(target) == 1
    curves[name] = {
        "drawing_index": index,
        "records": records,
        "paper_centerline": target[0]["value"],
        "stroke_width_points": drawing["width"],
        "dashes": drawing["dashes"],
    }
vectors = {}
for definition in ("primary", "aging_included_diagnostic"):
    for name in metrics["runs"][0][definition]:
        if name.startswith("death_percent/"):
            vectors[definition + "/" + name] = [
                row[definition][name] for row in metrics["runs"]
            ]
methods = [
    "inverted_cdf",
    "averaged_inverted_cdf",
    "nearest_even_order_statistic",
    "interpolated_inverted_cdf",
    "hazen",
    "weibull",
    "linear",
    "median_unbiased",
    "normal_unbiased",
]
comparisons = []
for series, values in vectors.items():
    for quantile_type, method in enumerate(methods, 1):
        if quantile_type == 3:
            ordered = sorted(values)
            quantiles = [ordered[round(len(values) * p) - 1] for p in (0.25, 0.5, 0.75)]
        else:
            quantiles = np.quantile(values, [0.25, 0.5, 0.75], method=method)
        for label, value in zip(
            ("first_quartile", "median", "third_quartile"), quantiles
        ):
            curve = curves[label]
            points = np.array([row["pdf_xy"] for row in curve["records"]])
            target = np.array(
                [box.x0 + 0.36 * box.width, box.y1 - value * box.height / 30]
            )
            delta = points[1:] - points[:-1]
            t = np.clip(
                ((target - points[:-1]) * delta).sum(axis=1)
                / (delta * delta).sum(axis=1),
                0,
                1,
            )
            distance = float(
                np.linalg.norm(target - points[:-1] - t[:, None] * delta, axis=1).min()
            )
            comparisons.append(
                {
                    "series": series,
                    "quantile_type": quantile_type,
                    "quantile": label,
                    "value": float(value),
                    "distance_points": distance,
                    "within_undashed_stroke_envelope": distance
                    <= curve["stroke_width_points"] / 2,
                }
            )
summary = {}
for family in ("primary/", "aging_included_diagnostic/"):
    selected = [row for row in comparisons if row["series"].startswith(family)]
    summary[family] = {
        "comparisons": len(selected),
        "inside_by_quantile": {
            label: sum(
                row["quantile"] == label and row["within_undashed_stroke_envelope"]
                for row in selected
            )
            for label in curves
        },
        "complete_triplets_inside": sum(
            all(
                row["within_undashed_stroke_envelope"]
                for row in selected
                if row["series"] == series and row["quantile_type"] == kind
            )
            for series in vectors
            if series.startswith(family)
            for kind in range(1, 10)
        ),
    }
output.mkdir()
(output / "vectors.json").write_text(json.dumps(vectors) + "\n")
report = {
    "metrics_sha256": hashlib.sha256(raw).hexdigest(),
    "axes_pdf_rectangle": list(box),
    "curves": curves,
    "comparisons": comparisons,
    "summary": summary,
    "scope": "Figure5 at selfishness0.36 only; dashed curves interpreted using Figure2's lower/upper-quartile convention. Full curve geometry ignores dash gaps, giving a generous envelope. Aging inclusion contradicts the paper's stated metric and remains a diagnostic. No definition or quantile method is selected after results; no completed-paper or negative-replication claim.",
}
(output / "comparison.json").write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps(summary, indent=2))
