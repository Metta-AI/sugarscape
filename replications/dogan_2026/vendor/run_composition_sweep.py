"""
run_composition_sweep.py — initial-composition sensitivity (Domain MC7).

Addresses the referee question: "Is the initial population composition
(120/40/20/20) driving the results?"  We test two alternative initial splits
bracketing the canonical baseline:

  low  automation:  frac_auto=0.05, frac_ai_aug=0.10  -> 160/20/10/10
  base (canonical): frac_auto=0.10, frac_ai_aug=0.20  -> 120/40/20/20  (in Part B)
  high automation:  frac_auto=0.15, frac_ai_aug=0.30  ->  80/60/30/30

For each alternative composition, thresholds (income, wealth-upper, UHI rate)
are RE-DERIVED from that composition's own k=0,m=0 baseline — i.e. policy is
calibrated to its own economy, the consistent design choice.  Each composition
is then run over the full 7 cells x 3 km x 5 seeds.

Outputs (under results/canonical/):
  composition_sweep.csv  — one row per (composition, km, cell, seed), same
                           column schema as part_b_stage5_main.csv plus a
                           'composition' label.

Horizon sensitivity is intentionally NOT run here (declined as a bounded
extension per the referee response).
"""

import os
import numpy as np
import pandas as pd

from sugarscape_ai_tax.model import SugarscapeAITax

os.makedirs("results/canonical", exist_ok=True)

MAIN_STEPS  = 300
SEEDS       = list(range(5))
THRESH_SEED = 42

KM_CASES = [
    {"label": "slow",     "k": 20, "m": 10},
    {"label": "balanced", "k": 10, "m": 10},
    {"label": "fast",     "k": 5,  "m": 20},
]
CELLS = [
    {"tax_regime": "none",              "redistribution_mode": "none",         "label": "baseline"},
    {"tax_regime": "labour",            "redistribution_mode": "ubi",          "label": "labour/ubi"},
    {"tax_regime": "labour",            "redistribution_mode": "means_tested", "label": "labour/means_tested"},
    {"tax_regime": "wealth",            "redistribution_mode": "ubi",          "label": "wealth/ubi"},
    {"tax_regime": "wealth",            "redistribution_mode": "means_tested", "label": "wealth/means_tested"},
    {"tax_regime": "displacement_levy", "redistribution_mode": "means_tested", "label": "disp_levy/means_tested"},
    {"tax_regime": "uhi_scenario",      "redistribution_mode": "none",         "label": "uhi_scenario"},
]

COMPOSITIONS = [
    {"label": "low",  "frac_autonomous": 0.05, "frac_ai_aug": 0.10},
    {"label": "high", "frac_autonomous": 0.15, "frac_ai_aug": 0.30},
]


def _wmean(df, mean_col, count_col="StarvationDeaths"):
    counts = df[count_col].astype(float)
    if counts.sum() == 0:
        return float("nan")
    return float((df[mean_col].astype(float) * counts).sum() / counts.sum())


def derive_thresholds(comp):
    """Re-derive income/wealth thresholds + UHI rate from this composition's
    own k=0,m=0 baseline (seed=42)."""
    fa, fai = comp["frac_autonomous"], comp["frac_ai_aug"]
    _m = SugarscapeAITax(tax_regime="none", redistribution_mode="none",
                         k=0, m=0, frac_autonomous=fa, frac_ai_aug=fai,
                         seed=THRESH_SEED)
    _m.run_model(200)
    _df = _m.datacollector.get_model_vars_dataframe()
    income_thr   = float(_df["MedianIncome"].iloc[199])
    wealth_upper = 2.0 * float(_df["MedianWealth"].iloc[199])

    _m2 = SugarscapeAITax(
        tax_regime="wealth", redistribution_mode="means_tested",
        k=10, m=10, frac_autonomous=fa, frac_ai_aug=fai,
        income_threshold=income_thr, wealth_threshold_lower=50,
        wealth_threshold_upper=wealth_upper, seed=THRESH_SEED,
    )
    _m2.run_model(MAIN_STEPS)
    _adf = _m2.datacollector.get_agent_vars_dataframe()
    _elig = _adf[_adf["TransferReceived"] > 0]["TransferReceived"]
    uhi_rate = 2.0 * (float(_elig.mean()) if len(_elig) > 0 else 1.0)
    return income_thr, wealth_upper, uhi_rate


def extract_row(df, comp_label, km_label, k, m, cell, seed):
    sc = int(df["StarvationDeaths"].sum())
    return {
        "composition": comp_label,
        "km_label": km_label, "k": k, "m": m,
        "cell_label": cell["label"],
        "tax_regime": cell["tax_regime"],
        "redistribution_mode": cell["redistribution_mode"],
        "seed": seed,
        "gini_final":     float(df["Gini"].iloc[-1]),
        "n_working_final":    int(df["n_WorkingHumanAgent"].iloc[-1]),
        "n_ai_aug_final":     int(df["n_AIAugmentedAgent"].iloc[-1]),
        "n_autonomous_final": int(df["n_AutonomousAgent"].iloc[-1]),
        "n_owner_final":      int(df["n_OwnerHumanAgent"].iloc[-1]),
        "working_wealth_share_final": float(df["WorkingHumanWealthShare"].iloc[-1]),
        "auto_wealth_share_final":    float(df["AutoWealthShare"].iloc[-1]),
        "owner_wealth_share_final":   float(df["OwnerWealthShare"].iloc[-1]),
        "starvation_deaths_total": sc,
        "deaths_sugar_only":       int(df["StarvationDeaths_SugarOnly"].sum()),
        "deaths_spice_only":       int(df["StarvationDeaths_SpiceOnly"].sum()),
        "deaths_both":             int(df["StarvationDeaths_Both"].sum()),
        "mean_wealth_at_death": _wmean(df, "MeanWealthAtStarvationDeath"),
        "displacement_conversions":  int(df["DisplacementConversions"].iloc[-1]),
        "reinstatement_conversions": int(df["ReinstatemntConversions"].iloc[-1]),
        "phi_min":  float(df["phi"].min()),
    }


rows = []
for comp in COMPOSITIONS:
    print("=" * 70)
    print(f"Composition '{comp['label']}'  "
          f"(frac_auto={comp['frac_autonomous']}, frac_ai_aug={comp['frac_ai_aug']})")
    print("=" * 70)
    inc, wup, uhi = derive_thresholds(comp)
    print(f"  thresholds: income={inc:.4f}  wealth_upper={wup:.4f}  uhi_rate={uhi:.4f}\n")

    total = len(KM_CASES) * len(CELLS) * len(SEEDS)
    n = 0
    for km in KM_CASES:
        for cell in CELLS:
            for seed in SEEDS:
                n += 1
                print(f"  [{n:3d}/{total}] {comp['label']:4s} {km['label']:8s} / "
                      f"{cell['label']:30s} seed={seed}", flush=True)
                kwargs = dict(
                    tax_regime=cell["tax_regime"],
                    redistribution_mode=cell["redistribution_mode"],
                    k=km["k"], m=km["m"],
                    frac_autonomous=comp["frac_autonomous"],
                    frac_ai_aug=comp["frac_ai_aug"],
                    income_threshold=inc, wealth_threshold_lower=50,
                    wealth_threshold_upper=wup, seed=seed,
                )
                if cell["tax_regime"] == "uhi_scenario":
                    kwargs["uhi_transfer_rate"] = uhi
                model = SugarscapeAITax(**kwargs)
                model.run_model(MAIN_STEPS)
                df = model.datacollector.get_model_vars_dataframe()
                rows.append(extract_row(df, comp["label"], km["label"],
                                        km["k"], km["m"], cell, seed))
    print()

pd.DataFrame(rows).to_csv("results/canonical/composition_sweep.csv", index=False)
print(f"Saved results/canonical/composition_sweep.csv  ({len(rows)} rows)")
