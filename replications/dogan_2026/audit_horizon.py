"""Reconstruct Table D.1 and its welfare ranking from all 45 horizon runs."""
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np
import pandas as pd

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("csv", type=Path)
parser.add_argument("provenance", choices=["author-deposit", "fresh-replay"])
parser.add_argument("output", type=Path)
args = parser.parse_args()
target_file = Path(__file__).with_name("manuscript-targets.json")
targets = json.loads(target_file.read_text())
frame = pd.read_csv(args.csv)
assert len(frame) == 45
keys = ["km_label", "cell_label", "seed"]
expected = {(speed, cell, seed) for speed in ["slow", "balanced", "fast"]
            for cell in ["baseline", "labour/means_tested", "wealth/means_tested"] for seed in range(5)}
assert set(frame[keys].itertuples(index=False, name=None)) == expected
assert not frame.duplicated(keys).any()
metrics = ["gini_300", "gini_600", "deaths_300", "deaths_600"]
assert np.isfinite(frame[metrics].to_numpy()).all()
assert frame[["gini_300", "gini_600"]].ge(0).all().all()
assert frame[["gini_300", "gini_600"]].le(1).all().all()
assert (frame.deaths_600 >= frame.deaths_300).all()
means = frame.groupby(["km_label", "cell_label"])[metrics].mean()
comparison = []
for row in targets["rows"]:
    cell = row["cell"].replace("labor/", "labour/").replace("means-tested", "means_tested")
    for metric in metrics:
        value = float(means.loc[(row["speed"], cell), metric])
        decimals = 3 if metric.startswith("gini") else 0
        comparison.append({"cell": cell, "speed": row["speed"], "metric": metric,
                           "mean": value, "published": row[metric],
                           "matches_printed_precision": f"{value:.{decimals}f}" == row[metric]})
ratios = []
for speed in ["slow", "balanced", "fast"]:
    baseline = means.loc[(speed, "baseline"), "deaths_600"]
    assert baseline > 0
    for cell in ["labour/means_tested", "wealth/means_tested"]:
        ratios.append({"speed": speed, "cell": cell,
                       "mortality_ratio_600": float(means.loc[(speed, cell), "deaths_600"] / baseline)})
report = {"provenance": args.provenance, "rows": len(frame), "table_cells": len(comparison),
          "input_sha256": hashlib.sha256(args.csv.read_bytes()).hexdigest(),
          "targets_sha256": hashlib.sha256(target_file.read_bytes()).hexdigest(),
          "comparison": comparison, "mortality_ratios": ratios,
          "interpretation": "Author-deposit agreement checks internal reporting only. Fresh-replay agreement additionally requires the pinned native execution manifest; neither alone completes the full paper."}
args.output.mkdir(parents=True, exist_ok=False)
(args.output / "table-d1.json").write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps({"table_cells": len(comparison), "matches": sum(r["matches_printed_precision"] for r in comparison),
                  "mortality_ratios": ratios}))
assert all(r["matches_printed_precision"] for r in comparison), "Printed table mismatch; inspect retained evidence"
