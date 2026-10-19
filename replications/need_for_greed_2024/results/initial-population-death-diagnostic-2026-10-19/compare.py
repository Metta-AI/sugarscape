"""Compare all predeclared initial-population death diagnostic quantiles."""

from pathlib import Path
import hashlib
import json
import sys

import fitz
import numpy as np

workspace, metrics_path, output = map(Path, sys.argv[1:])
assert not output.exists()
raw = metrics_path.read_bytes()
metrics = json.loads(raw)
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
for label, index in [("first_quartile", 67), ("median", 64), ("third_quartile", 76)]:
    drawing = drawings[index]
    points = [drawing["items"][0][1]]
    assert drawing["color"] == ((1, 0, 1) if label == "median" else (0, 0, 0))
    for item in drawing["items"]:
        assert item[0] == "l" and item[1] == points[-1]
        points.append(item[2])
    curves[label] = {
        "drawing_index": index,
        "points": [list(p) for p in points],
        "stroke_width": drawing["width"],
        "dashes": drawing["dashes"],
    }
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
output.mkdir()
summaries = []
for cohort in metrics:
    condition = cohort["condition"]
    assert (
        condition in (0.36, 0.37)
        and cohort["inputs"] == 100
        and cohort["initial_population"] == 250
    )
    vectors = {
        name: [r["values"][name] for r in cohort["runs"]]
        for name in cohort["runs"][0]["values"]
    }
    assert len(vectors) == 4
    comparisons = []
    for series, values in vectors.items():
        for kind, method in enumerate(methods, 1):
            quantiles = (
                [sorted(values)[round(len(values) * p) - 1] for p in (0.25, 0.5, 0.75)]
                if kind == 3
                else np.quantile(values, [0.25, 0.5, 0.75], method=method)
            )
            for label, value in zip(
                ["first_quartile", "median", "third_quartile"], quantiles
            ):
                curve = curves[label]
                points = np.array(curve["points"])
                target = np.array(
                    [box.x0 + condition * box.width, box.y1 - value * box.height / 30]
                )
                delta = points[1:] - points[:-1]
                t = np.clip(
                    ((target - points[:-1]) * delta).sum(axis=1)
                    / (delta * delta).sum(axis=1),
                    0,
                    1,
                )
                distance = float(
                    np.linalg.norm(
                        target - points[:-1] - t[:, None] * delta, axis=1
                    ).min()
                )
                vertex = [
                    p
                    for p in points
                    if abs((p[0] - box.x0) / box.width - condition) < 0.00004
                ]
                assert len(vertex) == 1
                comparisons.append(
                    {
                        "series": series,
                        "quantile_type": kind,
                        "quantile": label,
                        "value": float(value),
                        "paper_centerline": float(
                            (box.y1 - vertex[0][1]) * 30 / box.height
                        ),
                        "distance_points": distance,
                        "within_envelope": distance <= curve["stroke_width"] / 2,
                    }
                )
    report = {
        "condition": condition,
        "inputs": 100,
        "observations": cohort["observations"],
        "metrics_sha256": hashlib.sha256(raw).hexdigest(),
        "axes": list(box),
        "y_limits": [0, 30],
        "curves": curves,
        "comparisons": comparisons,
        "summary": {
            label: {
                "inside": sum(
                    r["within_envelope"] for r in comparisons if r["quantile"] == label
                ),
                "total": 36,
            }
            for label in curves
        },
        "scope": "Fixed initial population diagnostic; all predeclared conventions retained. Envelope distances ignore dash gaps. Not identification of historical plotting code or independent simulation.",
    }
    dest = output / str(condition)
    dest.mkdir()
    (dest / "comparison.json").write_text(json.dumps(report, indent=2) + "\n")
    (dest / "vectors.json").write_text(json.dumps(vectors) + "\n")
    summaries.append({"condition": condition, "summary": report["summary"]})
(output / "summary.json").write_text(json.dumps(summaries, indent=2) + "\n")
print(json.dumps(summaries))
