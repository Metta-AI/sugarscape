"""Reconstruct all Table 4 mortality means and coefficients of variation."""
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
target_file = Path(__file__).with_name("mortality-targets.json")
targets = json.loads(target_file.read_text())
frame = pd.read_csv(args.csv)
keys = ["km_label", "cell_label", "seed"]
labels = {"baseline": "baseline", "labor/UBI": "labour/ubi", "labor/means-tested": "labour/means_tested",
          "wealth/UBI": "wealth/ubi", "wealth/means-tested": "wealth/means_tested",
          "disp-levy/means-tested": "disp_levy/means_tested", "UHI scenario": "uhi_scenario"}
expected = {(speed, cell, seed) for speed in ["slow", "balanced", "fast"] for cell in labels.values() for seed in range(5)}
assert len(frame) == 105 and not frame.duplicated(keys).any()
assert set(frame[keys].itertuples(index=False, name=None)) == expected
metrics = ["starvation_deaths_total", "deaths_sugar_only", "deaths_spice_only", "deaths_both"]
assert np.isfinite(frame[metrics].to_numpy()).all()
assert frame[metrics].ge(0).all().all()
assert (frame[metrics] == frame[metrics].astype(int)).all().all()
assert (frame.starvation_deaths_total == frame.deaths_sugar_only + frame.deaths_spice_only + frame.deaths_both).all()
groups = frame.groupby(["km_label", "cell_label"]).starvation_deaths_total
means = groups.mean()
# Report both conventions explicitly; the printed table uses the sample standard deviation.
sample_cv = groups.std(ddof=1) / means
population_cv = groups.std(ddof=0) / means
assert means.gt(0).all()
comparison = []
for row in targets["rows"]:
    cell = labels[row["cell"]]
    for speed, values in row["values"].items():
        index = speed, cell
        mean, cv = float(means.loc[index]), float(sample_cv.loc[index])
        comparison.append({"cell": cell, "speed": speed, "mean": mean, "sample_cv": cv,
                           "population_cv": float(population_cv.loc[index]),
                           "published_mean": values["mean"], "published_cv": values["cv"],
                           "mean_matches": f"{mean:.1f}" == values["mean"],
                           "cv_matches": f"{cv:.3f}" == values["cv"]})
rankings = {speed: list(means.loc[speed].sort_values().index) for speed in ["slow", "balanced", "fast"]}
ratios = [{"speed": speed, "cell": cell, "mortality_ratio": float(means.loc[speed, cell] / means.loc[speed, "baseline"])}
          for speed in ["slow", "balanced", "fast"] for cell in ["labour/means_tested", "wealth/means_tested"]]
report = {"provenance": args.provenance, "input_sha256": hashlib.sha256(args.csv.read_bytes()).hexdigest(),
          "targets_sha256": hashlib.sha256(target_file.read_bytes()).hexdigest(), "rows": len(frame),
          "comparison": comparison, "rankings_lowest_first": rankings, "mortality_ratios": ratios,
          "scope": "Table4 and per-run cause accounting; author-deposit agreement alone is not a fresh replication."}
args.output.mkdir(parents=True, exist_ok=False)
(args.output / "table4.json").write_text(json.dumps(report, indent=2, allow_nan=False) + "\n")
print(json.dumps({"table_cells": 42, "matches": sum(r["mean_matches"] + r["cv_matches"] for r in comparison), "rankings": rankings}))
assert all(r["mean_matches"] and r["cv_matches"] for r in comparison), "Printed table mismatch; inspect report"
