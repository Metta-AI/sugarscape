"""Reconstruct Table C.1 and distinguish full rankings from top/bottom claims."""
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np
import pandas as pd

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("composition", type=Path)
parser.add_argument("canonical", type=Path)
parser.add_argument("provenance", choices=["author-deposit", "fresh-replay"])
parser.add_argument("output", type=Path)
args = parser.parse_args()
target_file = Path(__file__).with_name("composition-targets.json")
targets = json.loads(target_file.read_text())
labels = {"baseline": "baseline", "labor/UBI": "labour/ubi", "labor/means-tested": "labour/means_tested",
          "wealth/UBI": "wealth/ubi", "wealth/means-tested": "wealth/means_tested",
          "disp-levy/means-tested": "disp_levy/means_tested", "UHI scenario": "uhi_scenario"}
composition = pd.read_csv(args.composition)
canonical = pd.read_csv(args.canonical)
assert len(composition) == 210 and len(canonical) == 105
canonical["composition"] = "base"
keys = ["composition", "km_label", "cell_label", "seed"]
frame = pd.concat([composition, canonical], ignore_index=True)
expected = {(comp, speed, cell, seed) for comp in ["low", "base", "high"] for speed in ["slow", "balanced", "fast"]
            for cell in labels.values() for seed in range(5)}
assert not frame.duplicated(keys).any()
assert set(frame[keys].itertuples(index=False, name=None)) == expected
metrics = ["gini_final", "starvation_deaths_total", "deaths_sugar_only", "deaths_spice_only", "deaths_both"]
assert np.isfinite(frame[metrics].to_numpy()).all() and frame[metrics].ge(0).all().all()
assert frame.gini_final.le(1).all()
assert (frame.starvation_deaths_total == frame.deaths_sugar_only + frame.deaths_spice_only + frame.deaths_both).all()
means = frame.groupby(keys[:3])[["gini_final", "starvation_deaths_total"]].mean()
comparison = []
for target in targets["rows"]:
    cell = labels[target["cell"]]
    for comp in ["low", "base", "high"]:
        for metric, field, decimals in [("gini", "gini_final", 3), ("deaths", "starvation_deaths_total", 1)]:
            value = float(means.loc[(comp, target["speed"], cell), field])
            printed = target[f"{metric}_{comp}"]
            comparison.append({"composition": comp, "speed": target["speed"], "cell": cell, "metric": metric,
                               "measured": value, "published": printed, "matches": f"{value:.{decimals}f}" == printed})
rankings = []
for comp in ["low", "base", "high"]:
    for speed in ["slow", "balanced", "fast"]:
        gini = list(means.loc[(comp, speed)].gini_final.sort_values().index)
        deaths = list(means.loc[(comp, speed)].starvation_deaths_total.sort_values().index)
        rankings.append({"composition": comp, "speed": speed, "gini_lowest_first": gini, "mortality_lowest_first": deaths,
                         "baseline_highest_mortality": deaths[-1] == "baseline",
                         "two_pure_means_tested_lowest": set(deaths[:2]) == {"labour/means_tested", "wealth/means_tested"}})
inversions = []
for comp in ["low", "base", "high"]:
    slow = next(r for r in rankings if r["composition"] == comp and r["speed"] == "slow")["gini_lowest_first"]
    fast = next(r for r in rankings if r["composition"] == comp and r["speed"] == "fast")["gini_lowest_first"]
    for cell in ["labour/means_tested", "wealth/means_tested", "disp_levy/means_tested"]:
        first, last = slow.index(cell) + 1, fast.index(cell) + 1
        inversions.append({"composition": comp, "cell": cell, "slow_rank": first, "fast_rank": last, "rank_increases": last > first})
report = {"provenance": args.provenance, "composition_sha256": hashlib.sha256(args.composition.read_bytes()).hexdigest(),
          "canonical_sha256": hashlib.sha256(args.canonical.read_bytes()).hexdigest(),
          "targets_sha256": hashlib.sha256(target_file.read_bytes()).hexdigest(), "runs": len(frame),
          "comparison": comparison, "rankings": rankings, "slow_to_fast_rank_changes": inversions,
          "scope": "Unrounded five-seed means. Rank1 is lowest. Nine comparisons include the levy cell; the two pure means-tested cells alone give six. Full ordering and lowest-pair/highest-baseline claims are separate; no significance test."}
args.output.mkdir(parents=True, exist_ok=False)
(args.output / "table-c1.json").write_text(json.dumps(report, indent=2, allow_nan=False) + "\n")
print(json.dumps({"table_cells": len(comparison), "matches": sum(r["matches"] for r in comparison),
    "top_bottom_claim_matches": sum(r["baseline_highest_mortality"] and r["two_pure_means_tested_lowest"] for r in rankings),
    "distinct_mortality_orderings": len({tuple(r["mortality_lowest_first"]) for r in rankings}),
    "increasing_gini_ranks": sum(r["rank_increases"] for r in inversions),
    "exceptions": [r for r in inversions if not r["rank_increases"]]}))
assert all(r["matches"] for r in comparison), "Printed table mismatch; inspect retained evidence"
