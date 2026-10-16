"""Independently reconstruct manuscript Tables 1 and 6 and their rankings."""
import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("static", type=Path)
parser.add_argument("transition", type=Path)
parser.add_argument("provenance", choices=["author-deposit", "fresh-replay"])
parser.add_argument("output", type=Path)
args = parser.parse_args()
target_file = Path(__file__).with_name("static-uhi-targets.json")
targets = json.loads(target_file.read_text())
labels = {"baseline": "baseline", "labor/UBI": "labour/ubi", "labor/means-tested": "labour/means_tested",
          "wealth/UBI": "wealth/ubi", "wealth/means-tested": "wealth/means_tested",
          "disp-levy/means-tested": "disp_levy/means_tested", "UHI scenario": "uhi_scenario"}
static = pd.read_csv(args.static)
transition = pd.read_csv(args.transition)
assert len(static) == 25 and not static.duplicated(["cell_label", "seed"]).any()
assert set(static[["cell_label", "seed"]].itertuples(index=False, name=None)) == {
    (labels[t["cell"]], seed) for t in targets["table1"] for seed in range(5)}
assert static.k.eq(0).all() and static.m.eq(0).all()
keys = ["km_label", "cell_label", "seed"]
assert len(transition) == 105 and not transition.duplicated(keys).any()
assert set(transition[keys].itertuples(index=False, name=None)) == {
    (speed, cell, seed) for speed in ["slow", "balanced", "fast"] for cell in labels.values() for seed in range(5)}
metrics = ["gini_final", "starvation_deaths_total"]
for frame in [static, transition]:
    assert np.isfinite(frame[metrics].to_numpy()).all()
    assert frame.gini_final.between(0, 1).all() and frame.starvation_deaths_total.gt(0).all()
static_means = static.groupby("cell_label")[metrics].mean()
static_cv = static.groupby("cell_label")[metrics].std(ddof=1) / static_means
means = transition.groupby(keys[:2])[metrics].mean()
comparison = []
for target in targets["table1"]:
    cell = labels[target["cell"]]
    values = {"gini": (static_means.loc[cell, "gini_final"], 3),
              "gini_cv": (static_cv.loc[cell, "gini_final"], 3),
              "deaths": (static_means.loc[cell, "starvation_deaths_total"], 1),
              "deaths_cv": (static_cv.loc[cell, "starvation_deaths_total"], 3)}
    for metric, (value, precision) in values.items():
        comparison.append({"table": 1, "cell": cell, "metric": metric, "measured": float(value),
                           "published": target[metric], "matches": f"{value:.{precision}f}" == target[metric]})
for target in targets["table6"]:
    cell, speed = labels[target["cell"]], target["speed"]
    group = means.loc[(speed, cell)]
    baseline = means.loc[(speed, "baseline"), "starvation_deaths_total"]
    values = {"gini": (group.gini_final, 3), "deaths": (group.starvation_deaths_total, 1),
              "baseline_percent": (100 * group.starvation_deaths_total / baseline, 1)}
    for metric, (value, precision) in values.items():
        comparison.append({"table": 6, "cell": cell, "speed": speed, "metric": metric, "measured": float(value),
                           "published": target[metric], "matches": f"{value:.{precision}f}" == target[metric]})
paired = transition.pivot(index=["km_label", "seed"], columns="cell_label", values="starvation_deaths_total")
comparisons = []
for (speed, seed), row in paired.iterrows():
    for cell in ["labour/means_tested", "wealth/means_tested"]:
        comparisons.append({"speed": speed, "seed": int(seed), "cell": cell,
                            "means_tested_deaths": float(row[cell]), "uhi_deaths": float(row.uhi_scenario),
                            "uhi_has_more_deaths": bool(row.uhi_scenario > row[cell])})
report = {"provenance": args.provenance,
          "input_sha256": {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in [args.static, args.transition]},
          "targets_sha256": hashlib.sha256(target_file.read_bytes()).hexdigest(),
          "comparison": comparison, "uhi_paired_seed_comparisons": comparisons,
          "static_rankings_lowest_first": {metric: list(static_means[metric].sort_values().index) for metric in metrics},
          "static_cv_max": float(static_cv.to_numpy().max()),
          "static_prose_all_cv_below_013": bool((static_cv.to_numpy() < 0.13).all()),
          "static_all_cv_below_015": bool((static_cv.to_numpy() < 0.15).all()),
          "scope": "Printed cells and descriptive seed comparisons; no significance, causal, or whole-paper verdict."}
args.output.mkdir(parents=True, exist_ok=False)
(args.output / "tables1-and6.json").write_text(json.dumps(report, indent=2, allow_nan=False) + "\n")
print(json.dumps({"cells": len(comparison), "matches": sum(r["matches"] for r in comparison),
                  "uhi_more_deaths": sum(r["uhi_has_more_deaths"] for r in comparisons),
                  "paired_comparisons": len(comparisons), "static_cv_max": report["static_cv_max"]}))
assert all(r["matches"] for r in comparison), "Printed table mismatch; inspect retained report"
