"""Compare remaining direct-metric quartiles at both complete native conditions."""

from pathlib import Path
import hashlib
import json
import sys

import fitz
import numpy as np

workspace, output = map(Path, sys.argv[1:])
assert not output.exists()
study = workspace / "sugarscape-need-for-greed/replications/need_for_greed_2024/results"
paper = (
    workspace / "sugarscape-replication-evidence/papers/need-for-greed-author-2024.pdf"
)
assert (
    hashlib.sha256(paper.read_bytes()).hexdigest()
    == "d96fbf4e514207590a4fd38636cf47199781876f956b2c1c6e21381c167c921c"
)
document = fitz.open(paper)
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
summary = []
for condition, folder, observations in [
    (0.36, "selfishness036-metrics-2026-10-19", 490477),
    (0.37, "all-metric-comparison-2026-10-19", 495265),
]:
    raw = (study / folder / "metrics.json").read_bytes()
    metrics = json.loads(raw)
    independent_raw = (study / folder / "numpy-validation.json").read_bytes()
    independent = json.loads(independent_raw)
    assert metrics["inputs"] == 100 and metrics["observations"] == observations
    assert independent["metrics_sha256"] == hashlib.sha256(raw).hexdigest()
    assert (
        independent["native_runs"] == 100
        and independent["primary_values_checked"] == 2400
    )
    checked = {r["entry"]: r["primary"] for r in independent["runs"]}
    assert len(checked) == len({r["entry"] for r in metrics["runs"]}) == 100
    for row in metrics["runs"]:
        for name, value in row["values"].items():
            assert abs(value - checked[row["entry"]][name]) / max(1, abs(value)) < 1e-12
    for figure, page, axis, median, low, high, metric in [
        (3, 4, 92, 71, 0, 350, "meanWealth"),
        (4, 5, 44, 23, 10, 20, "agentMeanTimeToLive"),
        (6, 5, 127, 106, 0, 70, "meanAgeAtDeath"),
    ]:
        drawings = document[page].get_drawings()
        assert drawings[axis]["items"][0][0] == "re"
        box = drawings[axis]["rect"]
        curves = {}
        for label, index in [
            ("first_quartile", median + 3),
            ("median", median),
            ("third_quartile", median + 12),
        ]:
            drawing = drawings[index]
            assert drawing["color"] == ((1, 0, 1) if label == "median" else (0, 0, 0))
            assert len(drawing["items"]) == 100
            points = [drawing["items"][0][1]]
            for item in drawing["items"]:
                assert item[0] == "l" and item[1] == points[-1]
                points.append(item[2])
            assert all(
                abs((p.x - box.x0) / box.width - i / 100) < 0.00004
                for i, p in enumerate(points)
            )
            curves[label] = {
                "drawing_index": index,
                "points": [list(p) for p in points],
                "values": [
                    low + (box.y1 - p.y) * (high - low) / box.height for p in points
                ],
                "stroke_width": drawing["width"],
                "dashes": drawing["dashes"],
            }
        assert all(
            curves["first_quartile"]["values"][i]
            <= curves["median"]["values"][i]
            <= curves["third_quartile"]["values"][i]
            for i in range(101)
        )
        vectors = {
            name: [r["values"][name] for r in metrics["runs"]]
            for name in metrics["runs"][0]["values"]
            if name.startswith(metric + "/")
        }
        assert len(vectors) == 4
        comparisons = []
        for series, values in vectors.items():
            for kind, method in enumerate(methods, 1):
                quantiles = (
                    [
                        sorted(values)[round(len(values) * p) - 1]
                        for p in (0.25, 0.5, 0.75)
                    ]
                    if kind == 3
                    else np.quantile(values, [0.25, 0.5, 0.75], method=method)
                )
                for label, value in zip(
                    ["first_quartile", "median", "third_quartile"], quantiles
                ):
                    curve = curves[label]
                    points = np.array(curve["points"])
                    target = np.array(
                        [
                            box.x0 + condition * box.width,
                            box.y1 - (value - low) * box.height / (high - low),
                        ]
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
                    comparisons.append(
                        {
                            "series": series,
                            "quantile_type": kind,
                            "quantile": label,
                            "value": float(value),
                            "paper_centerline": curve["values"][round(condition * 100)],
                            "distance_points": distance,
                            "within_envelope": distance <= curve["stroke_width"] / 2,
                        }
                    )
        report = {
            "condition": condition,
            "inputs": 100,
            "observations": observations,
            "figure": figure,
            "metric": metric,
            "metrics_sha256": hashlib.sha256(raw).hexdigest(),
            "independent_metrics_sha256": hashlib.sha256(independent_raw).hexdigest(),
            "axes": list(box),
            "y_limits": [low, high],
            "curves": curves,
            "comparisons": comparisons,
            "summary": {
                label: {
                    "inside": sum(
                        r["within_envelope"]
                        for r in comparisons
                        if r["quantile"] == label
                    ),
                    "total": 36,
                }
                for label in curves
            },
            "scope": "Previously declared per-run mean conventions only. Nine quantile definitions; ignores dash gaps. Graphical agreement is not statistical equivalence or historical plotting-pipeline identification.",
        }
        destination = output / f"{condition}-{metric}"
        destination.mkdir()
        (destination / "comparison.json").write_text(
            json.dumps(report, indent=2) + "\n"
        )
        (destination / "vectors.json").write_text(json.dumps(vectors) + "\n")
        summary.append(
            {"condition": condition, "metric": metric, "summary": report["summary"]}
        )
(output / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
print(json.dumps(summary))
