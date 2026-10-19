"""Compare all six egoistic-model paper curves and diagnose the death-rate definition."""

import argparse
import hashlib
import json
from pathlib import Path

import fitz
import numpy as np

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("paper", type=Path)
parser.add_argument("timeseries", type=Path)
parser.add_argument("output", type=Path)
args = parser.parse_args()
paper = args.paper
source = args.timeseries
root = args.output
root.mkdir(parents=True, exist_ok=False)
assert (
    hashlib.sha256(paper.read_bytes()).hexdigest()
    == "56f25d6c9c3947954e29689a4fbd4c2ff0c09abd6515e631311939b747d4d51d"
)
pins = json.loads((source / "provenance.json").read_text())["files"]
for name in ["audit.json", "inputs.json", "independent-means.csv", "derived-means.csv"]:
    assert hashlib.sha256((source / name).read_bytes()).hexdigest() == pins[name], name
means = np.loadtxt(source / "independent-means.csv", delimiter=",", skiprows=1)
derived = np.loadtxt(source / "derived-means.csv", delimiter=",", skiprows=1)
pdf = fitz.open(paper)
# Cyan Egoist legend and axes visually verified on pages13/14; fixed protocol retained.
panels = [
    (4, 12, 27, 34, 1200, means[:, 1]),
    (5, 12, 71, 78, 25, means[:, 2]),
    (6, 12, 117, 124, 0.12, derived[:, 1]),
    (7, 13, 33, 40, 90, means[:, 6]),
    (8, 13, 83, 90, 160000, means[:, 5]),
    (9, 13, 131, 138, 350, derived[:, 2]),
]
results = []
for figure, page, frame_index, curve_index, maximum, series in panels:
    drawings = pdf[page].get_drawings()
    frame = drawings[frame_index]["rect"]
    curve = drawings[curve_index]
    assert curve["color"] == (0.0, 1.0, 1.0) and all(
        x[0] == "l" for x in curve["items"]
    )
    points = np.array(
        [tuple(curve["items"][0][1])] + [tuple(x[2]) for x in curve["items"]]
    )
    times = (points[:, 0] - frame.x0) / (frame.x1 - frame.x0) * 5000
    indices = np.rint(times).astype(int)
    assert (
        np.max(np.abs(times - indices)) < 0.2
        and indices[0] == 0
        and indices[-1] == 5000
    )
    expected_y = frame.y1 - series[indices] / maximum * (frame.y1 - frame.y0)
    error = np.abs(points[:, 1] - expected_y)
    extracted = (frame.y1 - points[:, 1]) / (frame.y1 - frame.y0) * maximum
    data = np.column_stack([indices, points, extracted, series[indices], error])
    np.savetxt(
        root / f"figure-{figure}-egoistic.csv",
        data,
        delimiter=",",
        header="timestep,pdf_x,pdf_y,extracted_value,reproduced_value,error_pdf_points",
        comments="",
    )
    results.append(
        {
            "figure": figure,
            "page": page + 1,
            "frame_index": frame_index,
            "curve_index": curve_index,
            "frame": list(frame),
            "y_range": [0, maximum],
            "vertices": len(points),
            "max_error_pdf_points": float(error.max()),
            "median_error_pdf_points": float(np.median(error)),
            "within_0_005_point": int(np.count_nonzero(error <= 0.005)),
            "threshold_pdf_points": 0.005,
            "last_extracted": float(extracted[-1]),
            "last_reproduced": float(series[-1]),
        }
    )
(root / "initial-comparison.json").write_text(json.dumps(results, indent=2) + "\n")
print(json.dumps(results, indent=2))

inputs = json.loads((source / "inputs.json").read_text())
causes = [
    "agentStarvationDeaths",
    "agentCombatDeaths",
    "agentDiseaseDeaths",
    "agentAgingDeaths",
]
sums = np.zeros((5001, 4), dtype=np.int64)
for seed, item in inputs.items():
    raw = (source / "native-inputs" / f"egoisticHalfLookaheadBinary{seed}.json").read_bytes()
    assert hashlib.sha256(raw).hexdigest() == item["record"]["trajectory_sha256"]
    rows = json.loads(raw)
    for row in rows:
        sums[row["timestep"]] += np.asarray([row[c] for c in causes], dtype=np.int64)
means = np.loadtxt(source / "independent-means.csv", delimiter=",", skiprows=1)
ratios = sums.sum(axis=1) / 500 / means[:, 1]
np.savetxt(
    root / "all-cause-deaths.csv",
    np.column_stack([np.arange(5001), sums / 500, ratios]),
    delimiter=",",
    header="timestep," + ",".join(causes) + ",all_deaths_per_population",
    comments="",
)
curve = np.loadtxt(root / "figure-6-egoistic.csv", delimiter=",", skiprows=1)
comparison = json.loads((root / "initial-comparison.json").read_text())[2]
y0 = comparison["frame"][3]
height = y0 - comparison["frame"][1]
expected = y0 - ratios[curve[:, 0].astype(int)] / 0.12 * height
errors = np.abs(curve[:, 2] - expected)
report = {
    "definition": "Sum starvation, combat, disease and aging deaths, divide by500 then divide by mean population. Same native trajectories; no simulation modification.",
    "vertices": len(errors),
    "max_error_pdf_points": float(errors.max()),
    "within_0_005_point": int(np.count_nonzero(errors <= 0.005)),
    "threshold_pdf_points": 0.005,
    "final_deaths_by_cause": dict(zip(causes, (sums[-1] / 500).tolist(), strict=True)),
    "final_all_cause_death_rate": float(ratios[-1]),
    "original_plotter_rate": float(
        np.loadtxt(source / "derived-means.csv", delimiter=",", skiprows=1)[-1, 1]
    ),
    "interpretation": "All-cause alternative fixed before Egoist curve comparison based on prior Raw discrepancy; neither historical plotting identity nor an independent preregistered claim.",
}
(root / "death-definition-diagnostic.json").write_text(
    json.dumps(report, indent=2) + "\n"
)
print(json.dumps(report, indent=2))
