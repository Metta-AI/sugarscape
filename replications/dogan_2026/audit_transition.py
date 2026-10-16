"""Reconstruct transition inequality and resource-exhaustion Tables 2 and 5."""
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
target_file = Path(__file__).with_name("transition-targets.json")
targets = json.loads(target_file.read_text())
frame = pd.read_csv(args.csv)
keys = ["km_label", "cell_label", "seed"]
labels = {"baseline": "baseline", "labor/UBI": "labour/ubi", "labor/means-tested": "labour/means_tested",
          "wealth/UBI": "wealth/ubi", "wealth/means-tested": "wealth/means_tested",
          "disp-levy/means-tested": "disp_levy/means_tested", "UHI scenario": "uhi_scenario"}
expected = {(speed, cell, seed) for speed in ["slow", "balanced", "fast"] for cell in labels.values() for seed in range(5)}
assert len(frame) == 105 and not frame.duplicated(keys).any()
assert set(frame[keys].itertuples(index=False, name=None)) == expected
fields = {"deaths": "starvation_deaths_total", "sugar": "deaths_sugar_only", "spice": "deaths_spice_only",
          "joint": "deaths_both", "stock": "mean_wealth_at_death", "single_percent": "single_percent"}
assert frame.starvation_deaths_total.gt(0).all()
assert (frame.starvation_deaths_total == frame.deaths_sugar_only + frame.deaths_spice_only + frame.deaths_both).all()
frame["single_percent"] = 100 * (frame.deaths_sugar_only + frame.deaths_spice_only) / frame.starvation_deaths_total
assert np.allclose(frame.single_percent, 100 * (1 - frame.frac_both), rtol=1e-10, atol=1e-10)
assert np.isfinite(frame[["gini_final", *fields.values()]].to_numpy()).all()
assert frame.gini_final.between(0, 1).all()
groups = frame.groupby(keys[:2])
means = groups[["gini_final", *fields.values()]].mean()
cv = groups.gini_final.std(ddof=1) / means.gini_final
comparison = []
for target in targets["table2"]:
    key = target["speed"], labels[target["cell"]]
    for metric, value in [("mean", float(means.loc[key, "gini_final"])), ("cv", float(cv.loc[key]))]:
        comparison.append({"table": 2, "speed": key[0], "cell": key[1], "metric": metric,
                           "measured": value, "published": target[metric], "matches": f"{value:.3f}" == target[metric]})
for target in targets["table5"]:
    key = target["speed"], labels[target["cell"]]
    for metric, field in fields.items():
        value = float(means.loc[key, field])
        comparison.append({"table": 5, "speed": key[0], "cell": key[1], "metric": metric,
                           "measured": value, "published": target[metric], "matches": f"{value:.1f}" == target[metric]})
rankings = {speed: list(means.loc[speed].gini_final.sort_values().index) for speed in ["slow", "balanced", "fast"]}
report = {"provenance": args.provenance, "input_sha256": hashlib.sha256(args.csv.read_bytes()).hexdigest(),
          "targets_sha256": hashlib.sha256(target_file.read_bytes()).hexdigest(), "rows": len(frame),
          "comparison": comparison, "gini_rankings_lowest_first": rankings,
          "single_resource_percent_per_run_range": [float(frame.single_percent.min()), float(frame.single_percent.max())],
          "single_resource_percent_five_seed_mean_range": [float(means.single_percent.min()), float(means.single_percent.max())],
          "interpretation": "Percentages average seed-specific fractions. Per-run ranges differ from five-seed means. Rankings are descriptive, not significance tests or causal proof."}
args.output.mkdir(parents=True, exist_ok=False)
(args.output / "tables2-and5.json").write_text(json.dumps(report, indent=2, allow_nan=False) + "\n")
print(json.dumps({"table_cells": len(comparison), "matches": sum(r["matches"] for r in comparison),
                  "per_run_percent_range": report["single_resource_percent_per_run_range"],
                  "mean_percent_range": report["single_resource_percent_five_seed_mean_range"]}))
assert all(r["matches"] for r in comparison), "Printed table mismatch; inspect retained report"
