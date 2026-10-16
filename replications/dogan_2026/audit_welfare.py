"""Reconstruct welfare-sensitivity Table B.1 and test its descriptive rankings."""
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np
import pandas as pd

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("main", type=Path)
parser.add_argument("sensitivity", type=Path)
parser.add_argument("provenance", choices=["author-deposit", "fresh-replay"])
parser.add_argument("output", type=Path)
args = parser.parse_args()
target_file = Path(__file__).with_name("welfare-targets.json")
targets = json.loads(target_file.read_text())
labels = {"baseline": "baseline", "labor/means-tested": "labour/means_tested", "wealth/means-tested": "wealth/means_tested",
          "disp-levy/means-tested": "disp_levy/means_tested", "UHI scenario": "uhi_scenario"}
keys = ["km_label", "cell_label", "seed"]
metrics = ["gini_final", "starvation_deaths_total", "trade_exchanges_mortal_auto"]
expected = {(speed, cell, seed) for speed in ["slow", "balanced", "fast"] for cell in labels.values() for seed in range(5)}
main = pd.read_csv(args.main)
linear = pd.read_csv(args.sensitivity)
assert len(main) == 105 and len(linear) == 75
geom = main[main.cell_label.isin(labels.values())]
for frame, mode in [(geom, "geometric_mean"), (linear, "linear")]:
    assert len(frame) == 75 and not frame.duplicated(keys).any()
    assert set(frame[keys].itertuples(index=False, name=None)) == expected
    assert set(frame.welfare_mode) == {mode}
    assert np.isfinite(frame[metrics].to_numpy()).all() and frame[metrics].ge(0).all().all()
    assert frame.gini_final.le(1).all()
    assert (frame.starvation_deaths_total == frame.deaths_sugar_only + frame.deaths_spice_only + frame.deaths_both).all()
g = geom.groupby(keys[:2])[metrics].mean()
l = linear.groupby(keys[:2])[metrics].mean()
comparison = []
effects = []
formats = {"gini_geom": ".3f", "gini_linear": ".3f", "gini_change": "+.3f", "deaths_geom": ".1f",
           "deaths_linear": ".1f", "deaths_percent": "+.1f", "trades_geom": ".0f", "trades_linear": ".0f"}
for target in targets["rows"]:
    key = target["speed"], labels[target["cell"]]
    a, b = g.loc[key], l.loc[key]
    assert a.starvation_deaths_total > 0 and a.trade_exchanges_mortal_auto > 0
    values = {"gini_geom": a.gini_final, "gini_linear": b.gini_final, "gini_change": b.gini_final - a.gini_final,
              "deaths_geom": a.starvation_deaths_total, "deaths_linear": b.starvation_deaths_total,
              "deaths_percent": 100 * (b.starvation_deaths_total / a.starvation_deaths_total - 1),
              "trades_geom": a.trade_exchanges_mortal_auto, "trades_linear": b.trade_exchanges_mortal_auto}
    effects.append({"speed": key[0], "cell": key[1], "gini_change": float(values["gini_change"]),
                    "mortality_percent_change": float(values["deaths_percent"]),
                    "cross_type_trade_percent_reduction": float(100 * (1 - b.trade_exchanges_mortal_auto / a.trade_exchanges_mortal_auto))})
    for metric, value in values.items():
        comparison.append({"speed": key[0], "cell": key[1], "metric": metric, "measured": float(value),
                           "published": target[metric], "matches": format(value, formats[metric]) == target[metric]})
rankings = []
for speed in ["slow", "balanced", "fast"]:
    for metric in ["gini_final", "starvation_deaths_total"]:
        first, second = list(g.loc[speed, metric].sort_values().index), list(l.loc[speed, metric].sort_values().index)
        rankings.append({"speed": speed, "metric": metric, "geometric": first, "linear": second, "unchanged": first == second})
report = {"provenance": args.provenance, "main_sha256": hashlib.sha256(args.main.read_bytes()).hexdigest(),
          "sensitivity_sha256": hashlib.sha256(args.sensitivity.read_bytes()).hexdigest(),
          "targets_sha256": hashlib.sha256(target_file.read_bytes()).hexdigest(), "comparison": comparison,
          "effects": effects, "rankings": rankings,
          "scope": "All15paired five-seed cells and120printed values; rank comparisons use unrounded means, not significance tests. No automatic whole-paper verdict."}
args.output.mkdir(parents=True, exist_ok=False)
(args.output / "table-b1.json").write_text(json.dumps(report, indent=2, allow_nan=False) + "\n")
print(json.dumps({"table_cells": len(comparison), "matches": sum(r["matches"] for r in comparison),
                  "rankings_unchanged": sum(r["unchanged"] for r in rankings), "rankings_checked": len(rankings)}))
assert all(r["matches"] for r in comparison), "Printed table mismatch; inspect retained evidence"
