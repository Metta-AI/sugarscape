"""
run_stage5_horizon.py — time-horizon robustness (Domain MC7).

Re-runs the no-intervention baseline and the two pure means-tested cells out to
600 steps (vs. the paper's 300) across the three canonical automation speeds and
five seeds, to test the manuscript's claim that the welfare ranking and the Gini
inversion are horizon-invariant — that a longer horizon rescales magnitudes
without altering rankings.

Thresholds are derived exactly as in run_canonical_sweep.py (seed-42 baseline).

Output: results/canonical/horizon_sweep.csv
  one row per (cell, km, seed) with Gini and deaths at step 300 and step 600.
"""
import os
import pandas as pd
from sugarscape_ai_tax.model import SugarscapeAITax

os.makedirs("results/canonical", exist_ok=True)
SEEDS = list(range(5))
KM = [{"label": "slow", "k": 20, "m": 10},
      {"label": "balanced", "k": 10, "m": 10},
      {"label": "fast", "k": 5, "m": 20}]
CELLS = [{"tax_regime": "none", "redistribution_mode": "none", "label": "baseline"},
         {"tax_regime": "labour", "redistribution_mode": "means_tested", "label": "labour/means_tested"},
         {"tax_regime": "wealth", "redistribution_mode": "means_tested", "label": "wealth/means_tested"}]

# thresholds (seed 42 baseline) — identical to canonical pipeline
_m = SugarscapeAITax(tax_regime="none", redistribution_mode="none", k=0, m=0, seed=42)
_m.run_model(200)
_df = _m.datacollector.get_model_vars_dataframe()
inc = float(_df["MedianIncome"].iloc[199]); wup = 2.0 * float(_df["MedianWealth"].iloc[199])
del _m, _df

rows = []
for km in KM:
    for cell in CELLS:
        for seed in SEEDS:
            print(f"  {km['label']:8s}/{cell['label']:20s} seed={seed} (600 steps)", flush=True)
            m = SugarscapeAITax(tax_regime=cell["tax_regime"], redistribution_mode=cell["redistribution_mode"],
                                k=km["k"], m=km["m"], income_threshold=inc,
                                wealth_threshold_lower=50, wealth_threshold_upper=wup, seed=seed)
            m.run_model(600)
            df = m.datacollector.get_model_vars_dataframe()
            rows.append({
                "km_label": km["label"], "cell_label": cell["label"], "seed": seed,
                "gini_300": float(df["Gini"].iloc[299]), "gini_600": float(df["Gini"].iloc[599]),
                "deaths_300": int(df["StarvationDeaths"].iloc[:300].sum()),
                "deaths_600": int(df["StarvationDeaths"].iloc[:600].sum()),
                "n_working_600": int(df["n_WorkingHumanAgent"].iloc[599]),
            })

pd.DataFrame(rows).to_csv("results/canonical/horizon_sweep.csv", index=False)
print(f"Saved results/canonical/horizon_sweep.csv ({len(rows)} rows)")
