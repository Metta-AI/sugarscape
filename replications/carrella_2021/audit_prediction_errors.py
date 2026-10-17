"""Locate concentrated held-out prediction errors without removing observations."""
import argparse
import csv
from collections import defaultdict
import json
import math
from pathlib import Path

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("predictions", type=Path)
parser.add_argument("output", type=Path)
args = parser.parse_args()
groups = defaultdict(list)
with args.predictions.open() as stream:
    for row in csv.DictReader(stream):
        truth, prediction = float(row["truth"]), float(row["prediction"])
        assert math.isfinite(truth) and math.isfinite(prediction)
        groups[(int(row["fold"]), row["parameter"])].append({
            "test_row": int(row["test_row"]), "truth": truth, "prediction": prediction,
            "squared_error": (prediction - truth) ** 2})
report = []
for (fold, parameter), rows in sorted(groups.items()):
    assert len({r["test_row"] for r in rows}) == len(rows)
    squared_error = sum(r["squared_error"] for r in rows)
    worst = sorted(rows, key=lambda r: r["squared_error"], reverse=True)[:5]
    report.append({"fold": fold, "parameter": parameter, "observations": len(rows),
                   "rmse": math.sqrt(squared_error / len(rows)), "squared_error": squared_error,
                   "five_largest_errors": worst,
                   "largest_fraction_squared_error": worst[0]["squared_error"] / squared_error})
with args.output.open("x") as stream:
    json.dump({"excluded_observations": 0, "groups": report}, stream, indent=2)
    stream.write("\n")
print(json.dumps([r for r in report if r["parameter"] == "wealth.reproduction"], indent=2))
