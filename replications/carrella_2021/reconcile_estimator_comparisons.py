"""Join audited independent estimates, author reruns, and every Table 8 cell.

This reconciles existing audits; it does not rerun fits or establish equivalence.
"""

import argparse
import csv
import hashlib
import json
import math
from pathlib import Path

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("manifest", type=Path)
parser.add_argument("output", type=Path)
args = parser.parse_args()
root = Path(__file__).resolve().parent
repo = root.parents[1]
manifest = json.loads(args.manifest.read_text())
names = {
    "rejection": "Rejection ABC",
    "sabc_4d": "Semi-automatic ABC 4D",
    "sabc_1d": "Semi-automatic ABC 1D",
    "loclin": "Local-linear ABC",
    "neuralnet": "Neural Network ABC",
    "lm": "Linear Regression",
    "loess": "GAM",
    "rf": "Quantile Random Forest",
    "rfboot": "Regression Random Forest",
}
hashes = {}


def record(path):
    content = path.read_bytes()
    hashes[str(path.relative_to(repo))] = hashlib.sha256(content).hexdigest()
    return content


published = json.loads(record(root / "published_table8.json"))
expected = {}
for row in published["rows"]:
    size = int(row[0].rsplit(" ", 1)[1].replace(",", ""))
    for method, value in zip(published["columns"][2:], row[2:]):
        key = (size, method, row[1])
        assert key not in expected
        expected[key] = value
assert len(expected) == 90
coverage = json.loads(record(root / manifest["author_coverage"]))
author = {}
for cell in coverage["cells"]:
    key = (cell["size"], cell["method"], cell["parameter"])
    assert key not in author and cell["published"] == expected[key]
    if cell["status"] == "computed":
        record(repo / cell["evidence"])
        assert hashes[cell["evidence"]] == cell["evidence_sha256"]
        assert math.isfinite(cell["measured"])
    else:
        assert cell["status"] == "not_reported" and expected[key] == "NA"
    author[key] = cell
assert author.keys() == expected.keys()
independent = {}
input_cells = 0
prediction_count = 0
for directory in manifest["independent_results"]:
    base = root / directory
    metric_bytes = record(base / "metrics.csv")
    checked_bytes = record(base / "validated-metrics.csv")
    provenance = json.loads(record(base / "fold-input-audit.json"))
    assert provenance["independent_summary_sha256"] == manifest["summary_sha256"]
    size = provenance["size"]
    assert provenance["folds"] == 5 and provenance["parameters"] == 5
    assert provenance["predictors"] == 146
    assert provenance["exact_training_and_testing_cells_verified"] == size * 5 * 151
    input_cells += provenance["exact_training_and_testing_cells_verified"]
    checked = {
        row["parameter"]: row
        for row in csv.DictReader(checked_bytes.decode().splitlines())
    }
    metrics = list(csv.DictReader(metric_bytes.decode().splitlines()))
    assert len(checked) == len(metrics) == 5
    for row in metrics:
        key = (int(row["size"]), names[row["method"]], row["parameter"])
        assert key[0] == size and key in expected and expected[key] != "NA"
        assert key not in independent
        audit = checked[row["parameter"]]
        assert int(audit["observations"]) == size
        for name in ["rmse", "coverage", "interval_width"]:
            assert math.isfinite(float(row[name]))
            assert math.isclose(
                float(row[name]), float(audit[name]), rel_tol=1e-12, abs_tol=1e-12
            )
        assert math.isclose(
            1 - float(row["rmse"]) / float(row["baseline_rmse"]),
            float(row["performance"]),
            rel_tol=1e-12,
            abs_tol=1e-12,
        )
        independent[key] = row
        prediction_count += size
rows = []
for key, value in expected.items():
    size, method, parameter = key
    entry = {"size": size, "method": method, "parameter": parameter, "published": value}
    if value == "NA":
        entry["status"] = "not_reported"
    else:
        entry["author_rerun"] = author[key]["measured"]
        entry["status"] = "independent_pending"
        if key in independent:
            result = independent[key]
            entry.update(
                status="paired",
                independent=float(result["performance"]),
                independent_minus_author=float(result["performance"])
                - author[key]["measured"],
                coverage=float(result["coverage"]),
                interval_width=float(result["interval_width"]),
            )
    rows.append(entry)
args.output.mkdir(exist_ok=False)
with (args.output / "comparison.csv").open("w") as stream:
    writer = csv.DictWriter(
        stream,
        fieldnames=[
            "size",
            "method",
            "parameter",
            "published",
            "status",
            "author_rerun",
            "independent",
            "independent_minus_author",
            "coverage",
            "interval_width",
        ],
    )
    writer.writeheader()
    writer.writerows(rows)
summary = {
    "table_cells": len(rows),
    "published_finite": sum(v != "NA" for v in expected.values()),
    "paired_scores": len(independent),
    "validated_predictions": prediction_count,
    "verified_training_testing_cells": input_cells,
    "pending": [r for r in rows if r["status"] == "independent_pending"],
    "input_sha256": hashes,
    "manifest_sha256": hashlib.sha256(args.manifest.read_bytes()).hexdigest(),
    "runner_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    "scope": "Reconciliation of retained input and prediction audits. No refitting, raw fold re-audit, statistical equivalence, or negative replication verdict. Different simulation random streams remain distinct.",
}
(args.output / "audit.json").write_text(json.dumps(summary, indent=2) + "\n")
print(
    json.dumps(
        {
            k: summary[k]
            for k in [
                "table_cells",
                "published_finite",
                "paired_scores",
                "validated_predictions",
                "verified_training_testing_cells",
            ]
        }
    )
)
