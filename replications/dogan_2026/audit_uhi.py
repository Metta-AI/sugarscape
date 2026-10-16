"""Audit the transfer-multiplier grid and reconcile the canonical two-times setting."""
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np
import pandas as pd

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("sweep", type=Path)
parser.add_argument("benchmark", type=Path)
parser.add_argument("provenance", choices=["author-deposit", "fresh-replay"])
parser.add_argument("output", type=Path)
args = parser.parse_args()
sweep = pd.read_csv(args.sweep)
benchmark = pd.read_csv(args.benchmark)
keys = ["km_label", "multiplier", "seed"]
expected = {(speed, multiplier, seed) for speed in ["slow", "balanced", "fast"] for multiplier in [1, 2, 3, 4] for seed in range(5)}
assert len(sweep) == 60 and not sweep.duplicated(keys).any()
assert set(sweep[keys].itertuples(index=False, name=None)) == expected
assert len(benchmark) == 105 and not benchmark.duplicated(["km_label", "cell_label", "seed"]).any()
assert np.isfinite(sweep[["uhi_rate", "gini_final", "deaths"]].to_numpy()).all()
assert sweep.gini_final.between(0, 1).all() and sweep.deaths.ge(0).all()
assert (sweep.deaths == sweep.deaths.astype(int)).all()
base_rates = sweep.uhi_rate / sweep.multiplier
assert np.allclose(base_rates, base_rates.iloc[0], rtol=1e-10, atol=1e-10)
original = benchmark[benchmark.cell_label == "uhi_scenario"].set_index(["km_label", "seed"])
means_tested = benchmark[benchmark.cell_label == "wealth/means_tested"].set_index(["km_label", "seed"])
assert len(original) == len(means_tested) == 15
assert set(original.index) == set(means_tested.index) == {(speed, seed) for speed in ["slow", "balanced", "fast"] for seed in range(5)}
two = sweep[sweep.multiplier == 2].set_index(["km_label", "seed"]).sort_index()
original = original.sort_index()
assert np.allclose(two.gini_final, original.gini_final, rtol=1e-10, atol=1e-10)
assert np.array_equal(two.deaths, original.starvation_deaths_total)
means = sweep.groupby(["km_label", "multiplier"])[["deaths", "gini_final"]].mean()
bench = means_tested.groupby("km_label").starvation_deaths_total.mean()
comparisons = []
for (speed, multiplier), row in means.iterrows():
    assert bench.loc[speed] > 0
    comparisons.append({"speed": speed, "multiplier": float(multiplier), "mean_deaths": float(row.deaths),
        "means_tested_mean_deaths": float(bench.loc[speed]), "mortality_ratio": float(row.deaths / bench.loc[speed]),
        "more_deaths_than_means_tested": bool(row.deaths > bench.loc[speed]), "mean_gini": float(row.gini_final)})
report = {"provenance": args.provenance, "sweep_sha256": hashlib.sha256(args.sweep.read_bytes()).hexdigest(),
          "benchmark_sha256": hashlib.sha256(args.benchmark.read_bytes()).hexdigest(), "runs": len(sweep),
          "canonical_two_times_rows_matched": len(two), "base_transfer_rate": float(base_rates.iloc[0]),
          "comparisons": comparisons,
          "interpretation": "Five-seed means and exact two-times reconciliation. Between-policy mean differences are descriptive; this is not a significance test or whole-paper verdict."}
args.output.mkdir(parents=True, exist_ok=False)
(args.output / "multiplier-audit.json").write_text(json.dumps(report, indent=2, allow_nan=False) + "\n")
print(json.dumps({"runs": len(sweep), "canonical_rows_matched": len(two),
                  "cells_with_more_mean_deaths_than_means_tested": sum(r["more_deaths_than_means_tested"] for r in comparisons),
                  "cells": len(comparisons), "mortality_ratio_range": [min(r["mortality_ratio"] for r in comparisons), max(r["mortality_ratio"] for r in comparisons)]}))
