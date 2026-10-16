"""
run_stage5_perseed_thresholds.py — robustness check: do the headline rankings
hold when income / wealth thresholds (and the UHI transfer rate) are re-derived
seed-by-seed instead of being fixed at the seed=42 baseline?

Both run_stage5.py and run_stage5_rob_starvation.py derive a single set of
thresholds from seed=42 and then sweep seeds 0–4 holding them fixed.  Referees
flagged this as a confound: a seed-specific shock to the seed=42 baseline could
bias every downstream cell.  This script instead derives thresholds inside the
seed loop.

It deliberately reuses the Session-B-instrumented model so the same per-resource
death columns are available.  Total runtime is roughly the same as the main
sweep plus 5 short baseline runs.

Outputs (under results/):
  stage5_perseed_thresholds.csv  — one row per (cell, km, seed) with the
      headline metrics + the thresholds actually used for that seed.
"""

import os
import numpy as np
import pandas as pd

from sugarscape_ai_tax.model import SugarscapeAITax

os.makedirs("results", exist_ok=True)

MAIN_STEPS = 300
SEEDS      = list(range(5))

KM_CASES = [
    {"label": "slow",     "k": 20, "m": 10},
    {"label": "balanced", "k": 10, "m": 10},
    {"label": "fast",     "k": 5,  "m": 20},
]
POLICY_CELLS = [
    {"tax_regime": "none",              "redistribution_mode": "none",         "label": "baseline"},
    {"tax_regime": "labour",            "redistribution_mode": "ubi",          "label": "labour/ubi"},
    {"tax_regime": "labour",            "redistribution_mode": "means_tested", "label": "labour/means_tested"},
    {"tax_regime": "wealth",            "redistribution_mode": "ubi",          "label": "wealth/ubi"},
    {"tax_regime": "wealth",            "redistribution_mode": "means_tested", "label": "wealth/means_tested"},
    {"tax_regime": "displacement_levy", "redistribution_mode": "means_tested", "label": "disp_levy/means_tested"},
    {"tax_regime": "uhi_scenario",      "redistribution_mode": "none",         "label": "uhi_scenario"},
]


def derive_thresholds(seed):
    """Run the no-tax / no-dynamics baseline at the given seed and extract
    income / wealth thresholds + UHI transfer rate (using the balanced
    wealth/means_tested reference run, also at this seed)."""
    _m = SugarscapeAITax(tax_regime="none", redistribution_mode="none",
                          k=0, m=0, seed=seed)
    _m.run_model(200)
    _df = _m.datacollector.get_model_vars_dataframe()
    income_thr = float(_df["MedianIncome"].iloc[199])
    wealth_upper = 2.0 * float(_df["MedianWealth"].iloc[199])

    _m2 = SugarscapeAITax(
        tax_regime="wealth", redistribution_mode="means_tested",
        k=10, m=10,
        income_threshold=income_thr,
        wealth_threshold_lower=50,
        wealth_threshold_upper=wealth_upper,
        seed=seed,
    )
    _m2.run_model(MAIN_STEPS)
    _adf = _m2.datacollector.get_agent_vars_dataframe()
    _elig = _adf[_adf["TransferReceived"] > 0]["TransferReceived"]
    uhi_rate = 2.0 * (float(_elig.mean()) if len(_elig) > 0 else 1.0)
    return income_thr, wealth_upper, uhi_rate


def _wmean(df, mean_col, count_col="StarvationDeaths"):
    counts = df[count_col].astype(float)
    if counts.sum() == 0:
        return float("nan")
    return float((df[mean_col].astype(float) * counts).sum() / counts.sum())


# ---------------------------------------------------------------------------
# Per-seed threshold derivation
# ---------------------------------------------------------------------------

per_seed = {}
print("Deriving thresholds per seed…")
for seed in SEEDS:
    inc, wup, uhi = derive_thresholds(seed)
    per_seed[seed] = {"income": inc, "wealth_upper": wup, "uhi": uhi}
    print(f"  seed={seed}  income={inc:.4f}  wealth_upper={wup:.4f}  uhi_rate={uhi:.4f}")
print()


def make_model(cell, km_case, seed):
    p = per_seed[seed]
    kwargs = dict(
        tax_regime=cell["tax_regime"],
        redistribution_mode=cell["redistribution_mode"],
        k=km_case["k"], m=km_case["m"],
        income_threshold=p["income"],
        wealth_threshold_lower=50,
        wealth_threshold_upper=p["wealth_upper"],
        seed=seed,
    )
    if cell["tax_regime"] == "uhi_scenario":
        kwargs["uhi_transfer_rate"] = p["uhi"]
    return SugarscapeAITax(**kwargs)


# ---------------------------------------------------------------------------
# Run 21 × 5 sweep
# ---------------------------------------------------------------------------

records = []
n_total = len(KM_CASES) * len(POLICY_CELLS) * len(SEEDS)
i = 0
for km in KM_CASES:
    for cell in POLICY_CELLS:
        for seed in SEEDS:
            i += 1
            print(f"  [{i:3d}/{n_total}] {km['label']:8s} / {cell['label']:30s}  "
                  f"seed={seed}", flush=True)
            m = make_model(cell, km, seed)
            m.run_model(MAIN_STEPS)
            df = m.datacollector.get_model_vars_dataframe()
            sc = int(df["StarvationDeaths"].sum())
            p = per_seed[seed]
            records.append({
                "km_label": km["label"], "k": km["k"], "m": km["m"],
                "cell_label": cell["label"],
                "tax_regime": cell["tax_regime"],
                "redistribution_mode": cell["redistribution_mode"],
                "seed": seed,
                "income_threshold_used":   p["income"],
                "wealth_upper_used":       p["wealth_upper"],
                "uhi_transfer_rate_used":  p["uhi"],
                "gini_final":          float(df["Gini"].iloc[-1]),
                "n_working_final":     int(df["n_WorkingHumanAgent"].iloc[-1]),
                "n_ai_aug_final":      int(df["n_AIAugmentedAgent"].iloc[-1]),
                "n_autonomous_final":  int(df["n_AutonomousAgent"].iloc[-1]),
                "n_owner_final":       int(df["n_OwnerHumanAgent"].iloc[-1]),
                "starvation_deaths_total": sc,
                "deaths_sugar_only": int(df["StarvationDeaths_SugarOnly"].sum()),
                "deaths_spice_only": int(df["StarvationDeaths_SpiceOnly"].sum()),
                "deaths_both":       int(df["StarvationDeaths_Both"].sum()),
                "mean_wealth_at_death": _wmean(df, "MeanWealthAtStarvationDeath"),
                "mean_sugar_at_death":  _wmean(df, "MeanSugarAtStarvationDeath"),
                "mean_spice_at_death":  _wmean(df, "MeanSpiceAtStarvationDeath"),
            })

pr_df = pd.DataFrame(records)
pr_df.to_csv("results/stage5_perseed_thresholds.csv", index=False)
print(f"\nSaved results/stage5_perseed_thresholds.csv  ({len(pr_df)} rows)")
