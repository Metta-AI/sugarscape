"""
run_stage5_D_sweep.py — sensitivity sweep over the displacement levy rate D.

The displacement-levy formula is
    levy_n = D * n / N0
where n is the ordinal of the displacement event and N0 the initial working
human population.  Both referees flagged that the headline claim that the
displacement levy is "self-calibrating" rests on the single value D=50.

This script varies D over {10, 25, 50, 100, 200} for the disp_levy/means_tested
cell, across the three canonical (k, m) cases and 5 seeds.  Total: 75 runs.

Outputs (under results/):
  stage5_D_sweep_perresource.csv  — one row per (D, km, seed) with the
      Session-B per-resource death aggregates plus Gini, working-human counts,
      treasury revenue, and mean wealth at death.
"""

import os
import numpy as np
import pandas as pd

from sugarscape_ai_tax.model import SugarscapeAITax

os.makedirs("results", exist_ok=True)

MAIN_STEPS = 300
SEEDS      = list(range(5))
THRESH_SEED = 42

KM_CASES = [
    {"label": "slow",     "k": 20, "m": 10},
    {"label": "balanced", "k": 10, "m": 10},
    {"label": "fast",     "k": 5,  "m": 20},
]

D_VALUES = [10.0, 25.0, 50.0, 100.0, 200.0]

# ---------------------------------------------------------------------------
# Threshold derivation (seed=42 baseline, matches run_stage5.py)
# ---------------------------------------------------------------------------

print("Deriving thresholds…")
_m = SugarscapeAITax(tax_regime="none", redistribution_mode="none", k=0, m=0, seed=THRESH_SEED)
_m.run_model(200)
_df = _m.datacollector.get_model_vars_dataframe()
income_threshold       = float(_df["MedianIncome"].iloc[199])
median_wealth_200      = float(_df["MedianWealth"].iloc[199])
wealth_threshold_upper = 2.0 * median_wealth_200
del _m, _df
print(f"  income_threshold={income_threshold:.4f}  wealth_upper={wealth_threshold_upper:.4f}\n")


def _wmean(df, mean_col, count_col="StarvationDeaths"):
    counts = df[count_col].astype(float)
    if counts.sum() == 0:
        return float("nan")
    return float((df[mean_col].astype(float) * counts).sum() / counts.sum())


records = []
n_total = len(D_VALUES) * len(KM_CASES) * len(SEEDS)
i = 0
for km in KM_CASES:
    for D in D_VALUES:
        for seed in SEEDS:
            i += 1
            print(f"  [{i:3d}/{n_total}] km={km['label']:8s} D={D:6.1f} seed={seed}", flush=True)
            m = SugarscapeAITax(
                tax_regime="displacement_levy",
                redistribution_mode="means_tested",
                k=km["k"], m=km["m"],
                income_threshold=income_threshold,
                wealth_threshold_lower=50,
                wealth_threshold_upper=wealth_threshold_upper,
                displacement_levy_rate=D,
                seed=seed,
            )
            m.run_model(MAIN_STEPS)
            df = m.datacollector.get_model_vars_dataframe()
            sc = int(df["StarvationDeaths"].sum())
            records.append({
                "km_label": km["label"], "k": km["k"], "m": km["m"],
                "D": D, "seed": seed,
                "gini_final":      float(df["Gini"].iloc[-1]),
                "n_working_final": int(df["n_WorkingHumanAgent"].iloc[-1]),
                "n_owner_final":   int(df["n_OwnerHumanAgent"].iloc[-1]),
                "displacements":   int(df["DisplacementConversions"].iloc[-1]),
                "starvation_deaths_total": sc,
                "deaths_sugar_only": int(df["StarvationDeaths_SugarOnly"].sum()),
                "deaths_spice_only": int(df["StarvationDeaths_SpiceOnly"].sum()),
                "deaths_both":       int(df["StarvationDeaths_Both"].sum()),
                "mean_wealth_at_death": _wmean(df, "MeanWealthAtStarvationDeath"),
                "mean_sugar_at_death":  _wmean(df, "MeanSugarAtStarvationDeath"),
                "mean_spice_at_death":  _wmean(df, "MeanSpiceAtStarvationDeath"),
                "total_tax_revenue":    float(df["TaxRevenue"].sum()),
                "total_redistribution": float(df["Redistribution"].sum()),
                "working_wealth_share_final": float(df["WorkingHumanWealthShare"].iloc[-1]),
                "owner_wealth_share_final":   float(df["OwnerWealthShare"].iloc[-1]),
                "auto_wealth_share_final":    float(df["AutoWealthShare"].iloc[-1]),
                "ai_aug_wealth_share_final":  float(df["AIAugWealthShare"].iloc[-1]),
            })

pr_df = pd.DataFrame(records)
pr_df.to_csv("results/stage5_D_sweep.csv", index=False)
print(f"\nSaved results/stage5_D_sweep.csv  ({len(pr_df)} rows)")
