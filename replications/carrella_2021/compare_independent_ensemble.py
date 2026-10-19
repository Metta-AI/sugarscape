"""Describe all original and independent statistics after complete ensemble audit.

Equal seed labels do not imply matched random streams. Distances are descriptive,
not equivalence tests or evidence of an implementation error by themselves.
"""

import argparse
import csv
import hashlib
import io
import json
from pathlib import Path

import numpy as np

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("author_source", type=Path)
parser.add_argument("reconciliation", type=Path)
parser.add_argument("output", type=Path)
args = parser.parse_args()
root = Path(__file__).resolve().parent
pins = json.loads((root / "source-audit.json").read_text())["sha256"]
coverage_bytes = (args.reconciliation / "coverage.json").read_bytes()
coverage = json.loads(coverage_bytes)
assert coverage["mode"] == "complete" and coverage["complete_original_ensemble"]
assert coverage["validated_inputs"] == coverage["required_inputs"] == 5000
assert coverage["missing_intervals"] == []
assert coverage["summary_file"] == "summary_statistics.csv"
for name, expected in coverage["source_sha256"].items():
    assert hashlib.sha256((root / name).read_bytes()).hexdigest() == expected
with (args.reconciliation / "row-index.csv").open(newline="") as stream:
    assert [int(row["original_row"]) for row in csv.DictReader(stream)] == list(
        range(5000)
    )

inputs = {}
for name in ["params_sugarscape.csv", "sugarscape.csv"]:
    content = (args.author_source / "data/sugarscape" / name).read_bytes()
    assert hashlib.sha256(content).hexdigest() == pins["data/sugarscape/" + name]
    inputs[name] = list(csv.DictReader(io.StringIO(content.decode())))
assert coverage["parameter_sha256"] == pins["data/sugarscape/params_sugarscape.csv"]
assert coverage["reference_sha256"] == pins["data/sugarscape/sugarscape.csv"]
summary_bytes = (args.reconciliation / "summary_statistics.csv").read_bytes()
assert hashlib.sha256(summary_bytes).hexdigest() == coverage["summary_sha256"]
independent_rows = list(csv.DictReader(io.StringIO(summary_bytes.decode())))
names = list(inputs["sugarscape.csv"][0])
assert len(names) == 150
assert all(list(row) == names for row in independent_rows)
original = np.array(
    [[float(row[name]) for name in names] for row in inputs["sugarscape.csv"]]
)
independent = np.array(
    [[float(row[name]) for name in names] for row in independent_rows]
)
assert original.shape == independent.shape == (5000, 150)
assert np.isfinite(original).all() and np.isfinite(independent).all()
parameters = inputs["params_sugarscape.csv"]
assert len(parameters) == 5000
parameter_names = [name for name in parameters[0] if name != "random-seed"]
assert len(parameter_names) == 5

# Define conditioning exclusively from original parameter inputs, not outcomes.
groups = [("all", -1, "", "", np.arange(5000))]
bin_metadata = {}
for name in parameter_names:
    values = np.array([float(row[name]) for row in parameters])
    assert np.isfinite(values).all() and values.min() < values.max()
    edges = np.linspace(values.min(), values.max(), 11)
    assignments = np.searchsorted(edges[1:-1], values, side="right")
    bin_metadata[name] = {
        "edges": edges.tolist(),
        "counts": np.bincount(assignments, minlength=10).tolist(),
    }
    for index in range(10):
        members = np.flatnonzero(assignments == index)
        assert len(members) > 0
        groups.append((name, index, edges[index], edges[index + 1], members))

args.output.mkdir(parents=True, exist_ok=False)
with (args.output / "comparisons.csv").open("x", newline="") as stream:
    writer = csv.writer(stream)
    writer.writerow(
        [
            "condition_parameter",
            "bin",
            "lower",
            "upper",
            "inputs",
            "statistic",
            "original_mean",
            "independent_mean",
            "mean_difference",
            "original_std",
            "independent_std",
            "original_q05",
            "independent_q05",
            "original_median",
            "independent_median",
            "original_q95",
            "independent_q95",
            "wasserstein_distance",
        ]
    )
    for parameter, index, low, high, members in groups:
        a, b = original[members], independent[members]
        aq = np.quantile(a, [0.05, 0.5, 0.95], axis=0, method="linear")
        bq = np.quantile(b, [0.05, 0.5, 0.95], axis=0, method="linear")
        # Equal sample sizes: empirical one-dimensional Wasserstein distance.
        distance = np.mean(np.abs(np.sort(a, axis=0) - np.sort(b, axis=0)), axis=0)
        am, bm = a.mean(axis=0), b.mean(axis=0)
        ast, bst = a.std(axis=0), b.std(axis=0)
        for column, name in enumerate(names):
            writer.writerow(
                [
                    parameter,
                    index,
                    low,
                    high,
                    len(members),
                    name,
                    am[column],
                    bm[column],
                    bm[column] - am[column],
                    ast[column],
                    bst[column],
                    aq[0, column],
                    bq[0, column],
                    aq[1, column],
                    bq[1, column],
                    aq[2, column],
                    bq[2, column],
                    distance[column],
                ]
            )

(args.output / "analysis.json").write_text(
    json.dumps(
        {
            "inputs": 5000,
            "statistics": 150,
            "comparison_rows": 7650,
            "coverage_sha256": hashlib.sha256(coverage_bytes).hexdigest(),
            "independent_summary_sha256": coverage["summary_sha256"],
            "reference_sha256": coverage["reference_sha256"],
            "parameter_sha256": coverage["parameter_sha256"],
            "analyzer_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            "numpy": np.__version__,
            "conditioning": bin_metadata,
            "bin_rule": "Ten equal-width bins over each original parameter range; left-closed/right-open, final bin includes maximum. Other parameters are not held fixed.",
            "scope": "All 150 empirical distributions, globally and conditioned on each of five input parameters. Population standard deviations and linear-interpolated quantiles. Descriptive distances only; no post-hoc acceptance margin, p-value, paired-random-stream assumption, or paper verdict.",
            "comparisons_sha256": hashlib.sha256(
                (args.output / "comparisons.csv").read_bytes()
            ).hexdigest(),
        },
        indent=2,
    )
    + "\n"
)
print(args.output.resolve())
