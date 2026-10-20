"""Distinguish per-run population means from temporal pooled-population quantiles."""

from pathlib import Path
import hashlib
import json
import math
import sys
import tarfile

import fitz
import numpy as np

workspace, output = map(Path, sys.argv[1:])
assert not output.exists()
study = workspace / "sugarscape-need-for-greed/replications/need_for_greed_2024/results"
paths = {
    "cohort": study / "selfishness037-reuse-2026-10-19/audit.json",
    "metrics": study / "all-metric-comparison-2026-10-19/metrics.json",
    "curves": study / "figure2-population-2026-10-19/comparison.json",
}
raw = {name: path.read_bytes() for name, path in paths.items()}
data = {name: json.loads(value) for name, value in raw.items()}
paper = (
    workspace / "sugarscape-replication-evidence/papers/need-for-greed-author-2024.pdf"
)
assert hashlib.sha256(paper.read_bytes()).hexdigest() == data["curves"]["paper_sha256"]
assert (
    hashlib.sha256(raw["cohort"]).hexdigest() == data["metrics"]["cohort_audit_sha256"]
)
drawings = fitz.open(paper)[4].get_drawings()
for curve in data["curves"]["curves"].values():
    drawing = drawings[curve["drawing_index"]]
    points = [drawing["items"][0][1]] + [item[2] for item in drawing["items"]]
    assert [list(point) for point in points] == [
        row["pdf_xy"] for row in curve["records"]
    ]
    assert drawing["width"] == curve["stroke_width_points"]

groups = {}
for row in data["cohort"]["runs"]:
    groups.setdefault(row["native_archive"], {})[
        row["manifest_member"].rsplit("/", 1)[0] + "/trajectory.json"
    ] = row
matrix = np.zeros((100, 5001))
available = np.zeros((100, 5001), dtype=bool)
per_run = {
    name: []
    for name in data["metrics"]["runs"][0]["values"]
    if name.startswith("population/")
}
metrics = {row["entry"]: row for row in data["metrics"]["runs"]}
seen = set()
for archive_name, wanted in sorted(groups.items()):
    path = workspace / "sugarscape-blueprints" / archive_name
    assert (
        hashlib.sha256(path.read_bytes()).hexdigest()
        == data["cohort"]["native_archive_sha256"][archive_name]
    )
    with tarfile.open(path, "r|gz") as archive:
        for member in archive:
            if member.name not in wanted:
                continue
            expected = wanted[member.name]
            assert expected["entry"] not in seen
            content = archive.extractfile(member).read()
            assert hashlib.sha256(content).hexdigest() == expected["trajectory_sha256"]
            rows = json.loads(content)
            assert len(rows) == expected["observations"]
            assert [row["timestep"] for row in rows] == list(range(len(rows)))
            assert len(rows) == 5001 or rows[-1]["population"] == 0
            population = np.array([row["population"] for row in rows], dtype=float)
            assert np.isfinite(population).all()
            index = len(seen)
            matrix[index, : len(rows)] = population
            available[index, : len(rows)] = True
            seen.add(expected["entry"])
            for name in per_run:
                start = int(name.endswith("excluding_initial"))
                selected = (
                    population[start:]
                    if "/observed/" in name
                    else matrix[index, start:]
                )
                value = float(selected.mean())
                assert math.isclose(
                    value,
                    metrics[expected["entry"]]["values"][name],
                    rel_tol=1e-12,
                    abs_tol=1e-12,
                )
                per_run[name].append(value)
assert len(seen) == 100 and int(available.sum()) == 495265
vectors = {"per_run/" + name: values for name, values in per_run.items()}
for convention, values in [
    ("zero_extended", matrix.mean(axis=0)),
    ("observed", matrix.sum(axis=0) / available.sum(axis=0)),
]:
    for start in (0, 1):
        name = "excluding_initial" if start else "including_initial"
        vectors[f"pooled_time/{convention}/{name}"] = values[start:].tolist()

methods = [
    "inverted_cdf",
    "averaged_inverted_cdf",
    "closest_observation",
    "interpolated_inverted_cdf",
    "hazen",
    "weibull",
    "linear",
    "median_unbiased",
    "normal_unbiased",
]
x0, y0, x1, y1 = data["curves"]["axes_pdf_rectangle"]
reports = []
for name, values in vectors.items():
    for quantile_type, method in enumerate(methods, 1):
        quantiles = np.quantile(values, [0.25, 0.5, 0.75], method=method)
        for label, value in zip(
            ["first_quartile", "median", "third_quartile"], quantiles
        ):
            curve = data["curves"]["curves"][label]
            points = np.array([row["pdf_xy"] for row in curve["records"]])
            target = np.array([x0 + 0.37 * (x1 - x0), y1 - value * (y1 - y0) / 1400])
            segments = points[1:] - points[:-1]
            parameter = np.clip(
                ((target - points[:-1]) * segments).sum(axis=1)
                / (segments * segments).sum(axis=1),
                0,
                1,
            )
            distance = float(
                np.linalg.norm(
                    target - points[:-1] - parameter[:, None] * segments, axis=1
                ).min()
            )
            reports.append(
                {
                    "series": name,
                    "quantile_type": quantile_type,
                    "numpy_method": method,
                    "quantile": label,
                    "value": float(value),
                    "paper_centerline": curve["records"][37]["population_centerline"],
                    "distance_points": distance,
                    "within_undashed_stroke_envelope": distance
                    <= curve["stroke_width_points"] / 2,
                }
            )
output.mkdir()
(output / "vectors.json").write_text(json.dumps(vectors) + "\n")
summary = {
    family: {
        "comparisons": sum(row["series"].startswith(family) for row in reports),
        "within_undashed_stroke_envelope": sum(
            row["series"].startswith(family) and row["within_undashed_stroke_envelope"]
            for row in reports
        ),
    }
    for family in ["per_run/", "pooled_time/"]
}
report = {
    "source_sha256": {
        name: hashlib.sha256(value).hexdigest() for name, value in raw.items()
    },
    "vectors_sha256": hashlib.sha256(
        (output / "vectors.json").read_bytes()
    ).hexdigest(),
    "inputs": 100,
    "observations": int(available.sum()),
    "comparisons": reports,
    "summary": summary,
    "scope": "Population at selfishness0.37 only. Nine standard quantile definitions, both initial-row conventions and two extinction denominators. Distance ignores dash gaps, so inclusion is only a generous geometric envelope; exclusion rules out painted-curve agreement. This does not identify historical plotting code or validate other metrics, conditions, confidence intervals, or the full paper.",
}
(output / "comparison.json").write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps(summary))
