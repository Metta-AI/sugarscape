"""
run_canonical_sweep.py — single source of truth for all paper tables.

Three sub-sweeps, all on the same (current, torus-fixed, Session-B-instrumented)
model, with 5 seeds (0..4):

  Part A — Stage 4 static composition (k=0, m=0)
    5 cells × 5 seeds = 25 runs  → Table 1
    Cells: baseline, labour/ubi, labour/means_tested,
           wealth/ubi, wealth/means_tested

  Part B — Stage 5 transition dynamics (3 km × 7 cells)
    7 cells × 3 km × 5 seeds = 105 runs  → Tables 2–6
    Cells: baseline, labour/ubi, labour/means_tested,
           wealth/ubi, wealth/means_tested,
           disp_levy/means_tested, uhi_scenario

  Part C — Autonomous-welfare sensitivity (LINEAR welfare on autonomous)
    5 cells × 3 km × 5 seeds = 75 runs  → §2.4 appendix sensitivity
    Cells: baseline, labour/means_tested, wealth/means_tested,
           disp_levy/means_tested, uhi_scenario

Threshold derivation: seed=42 baseline (same as Session B; the per-seed
robustness check already confirmed rankings are preserved).

Outputs (under results/canonical/):
  part_a_stage4_static.csv         — Table 1 source
  part_b_stage5_main.csv           — Tables 2–6 source (one row per run)
  part_b_agent_step300.csv         — Gini-decomposition source (one row per agent)
  part_c_welfare_sensitivity.csv   — §2.4 sensitivity source

Each row includes every column needed by the analysis scripts so that no
table in the final paper is built from a different model version.
"""

import os
import numpy as np
import pandas as pd

from sugarscape_ai_tax.model import SugarscapeAITax

os.makedirs("results/canonical", exist_ok=True)

MAIN_STEPS = 300
SEEDS      = list(range(5))
THRESH_SEED = 42

KM_CASES = [
    {"label": "slow",     "k": 20, "m": 10},
    {"label": "balanced", "k": 10, "m": 10},
    {"label": "fast",     "k": 5,  "m": 20},
]

STAGE4_CELLS = [
    {"tax_regime": "none",   "redistribution_mode": "none",         "label": "baseline"},
    {"tax_regime": "labour", "redistribution_mode": "ubi",          "label": "labour/ubi"},
    {"tax_regime": "labour", "redistribution_mode": "means_tested", "label": "labour/means_tested"},
    {"tax_regime": "wealth", "redistribution_mode": "ubi",          "label": "wealth/ubi"},
    {"tax_regime": "wealth", "redistribution_mode": "means_tested", "label": "wealth/means_tested"},
]

STAGE5_CELLS = STAGE4_CELLS + [
    {"tax_regime": "displacement_levy", "redistribution_mode": "means_tested", "label": "disp_levy/means_tested"},
    {"tax_regime": "uhi_scenario",      "redistribution_mode": "none",         "label": "uhi_scenario"},
]

SENSITIVITY_CELLS = [
    {"tax_regime": "none",              "redistribution_mode": "none",         "label": "baseline"},
    {"tax_regime": "labour",            "redistribution_mode": "means_tested", "label": "labour/means_tested"},
    {"tax_regime": "wealth",            "redistribution_mode": "means_tested", "label": "wealth/means_tested"},
    {"tax_regime": "displacement_levy", "redistribution_mode": "means_tested", "label": "disp_levy/means_tested"},
    {"tax_regime": "uhi_scenario",      "redistribution_mode": "none",         "label": "uhi_scenario"},
]

# ---------------------------------------------------------------------------
# Threshold derivation (seed=42 baseline; per-seed run already confirmed
# rankings are preserved across seed choice)
# ---------------------------------------------------------------------------

print("[setup] Deriving thresholds from seed=42 baseline…")
_m = SugarscapeAITax(tax_regime="none", redistribution_mode="none",
                     k=0, m=0, seed=THRESH_SEED)
_m.run_model(200)
_df = _m.datacollector.get_model_vars_dataframe()
income_threshold       = float(_df["MedianIncome"].iloc[199])
wealth_threshold_upper = 2.0 * float(_df["MedianWealth"].iloc[199])
del _m, _df

print("[setup] Deriving UHI transfer rate (balanced wealth/means_tested reference)…")
_m2 = SugarscapeAITax(
    tax_regime="wealth", redistribution_mode="means_tested",
    k=10, m=10,
    income_threshold=income_threshold, wealth_threshold_lower=50,
    wealth_threshold_upper=wealth_threshold_upper, seed=THRESH_SEED,
)
_m2.run_model(MAIN_STEPS)
_adf = _m2.datacollector.get_agent_vars_dataframe()
_elig = _adf[_adf["TransferReceived"] > 0]["TransferReceived"]
uhi_transfer_rate = 2.0 * (float(_elig.mean()) if len(_elig) > 0 else 1.0)
del _m2, _adf, _elig

print(f"[setup] income_threshold={income_threshold:.4f}  "
      f"wealth_upper={wealth_threshold_upper:.4f}  "
      f"uhi_rate={uhi_transfer_rate:.4f}\n")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _wmean(df, mean_col, count_col="StarvationDeaths"):
    counts = df[count_col].astype(float)
    if counts.sum() == 0:
        return float("nan")
    return float((df[mean_col].astype(float) * counts).sum() / counts.sum())


def make_model(cell, k, m, seed, welfare_mode="geometric_mean"):
    kwargs = dict(
        tax_regime=cell["tax_regime"],
        redistribution_mode=cell["redistribution_mode"],
        k=k, m=m,
        income_threshold=income_threshold,
        wealth_threshold_lower=50,
        wealth_threshold_upper=wealth_threshold_upper,
        autonomous_welfare_mode=welfare_mode,
        seed=seed,
    )
    if cell["tax_regime"] == "uhi_scenario":
        kwargs["uhi_transfer_rate"] = uhi_transfer_rate
    return SugarscapeAITax(**kwargs)


def extract_row(df, km_label, k, m, cell, seed, welfare_mode):
    sc = int(df["StarvationDeaths"].sum())
    return {
        "km_label": km_label, "k": k, "m": m,
        "cell_label": cell["label"],
        "tax_regime": cell["tax_regime"],
        "redistribution_mode": cell["redistribution_mode"],
        "seed": seed,
        "welfare_mode": welfare_mode,

        # Headline
        "gini_final":     float(df["Gini"].iloc[-1]),
        "gini_100":       float(df["Gini"].iloc[99]) if len(df) > 99 else float("nan"),

        # Population
        "n_working_final":    int(df["n_WorkingHumanAgent"].iloc[-1]),
        "n_ai_aug_final":     int(df["n_AIAugmentedAgent"].iloc[-1]),
        "n_autonomous_final": int(df["n_AutonomousAgent"].iloc[-1]),
        "n_owner_final":      int(df["n_OwnerHumanAgent"].iloc[-1]),

        # Wealth shares
        "working_wealth_share_final": float(df["WorkingHumanWealthShare"].iloc[-1]),
        "ai_aug_wealth_share_final":  float(df["AIAugWealthShare"].iloc[-1]),
        "auto_wealth_share_final":    float(df["AutoWealthShare"].iloc[-1]),
        "owner_wealth_share_final":   float(df["OwnerWealthShare"].iloc[-1]),

        # Deaths
        "starvation_deaths_total": sc,
        "natural_deaths_total":    int(df["NaturalDeaths"].sum()),
        "deaths_sugar_only":       int(df["StarvationDeaths_SugarOnly"].sum()),
        "deaths_spice_only":       int(df["StarvationDeaths_SpiceOnly"].sum()),
        "deaths_both":             int(df["StarvationDeaths_Both"].sum()),
        "frac_sugar_only": (df["StarvationDeaths_SugarOnly"].sum() / sc) if sc > 0 else float("nan"),
        "frac_spice_only": (df["StarvationDeaths_SpiceOnly"].sum() / sc) if sc > 0 else float("nan"),
        "frac_both":       (df["StarvationDeaths_Both"].sum() / sc) if sc > 0 else float("nan"),
        "mean_wealth_at_death": _wmean(df, "MeanWealthAtStarvationDeath"),
        "mean_sugar_at_death":  _wmean(df, "MeanSugarAtStarvationDeath"),
        "mean_spice_at_death":  _wmean(df, "MeanSpiceAtStarvationDeath"),

        # Transition dynamics
        "displacement_conversions":   int(df["DisplacementConversions"].iloc[-1]),
        "reinstatement_conversions":  int(df["ReinstatemntConversions"].iloc[-1]),

        # Trade
        "trade_exchanges_total":         int(df["TradeExchanges"].sum()),
        "trade_exchanges_mortal_auto":   int(df["TradeExchanges_MortalAuto"].sum()),

        # Treasury / fiscal
        "total_tax_revenue":      float(df["TaxRevenue"].sum()),
        "total_redistribution":   float(df["Redistribution"].sum()),
        "total_labour_tax_rev":   float(df["LabourTaxRevenue"].sum()),
        "total_wealth_tax_rev":   float(df["WealthTaxRevenue"].sum()),
        "total_ownerless_xfers":  float(df["OwnerlessTransfers"].sum()),
        "treasury_final":         float(df["Treasury"].iloc[-1]),

        # Resource dynamics
        "phi_min":            float(df["phi"].min()),
        "phi_mean":           float(df["phi"].mean()),
        "mean_regen_rate":    float(df["MeanRegenerationRate"].mean()),
    }


# ---------------------------------------------------------------------------
# Part A — Stage 4 static composition (k=0, m=0)
# ---------------------------------------------------------------------------

print("=" * 70)
print("Part A — Stage 4 static composition (k=0, m=0)")
print("=" * 70)

part_a_rows = []
total = len(STAGE4_CELLS) * len(SEEDS)
n = 0
for cell in STAGE4_CELLS:
    for seed in SEEDS:
        n += 1
        print(f"  [{n:3d}/{total}] {cell['label']:30s}  seed={seed}", flush=True)
        m = make_model(cell, k=0, m=0, seed=seed)
        m.run_model(MAIN_STEPS)
        df = m.datacollector.get_model_vars_dataframe()
        part_a_rows.append(extract_row(df, "static", 0, 0, cell, seed,
                                       "geometric_mean"))

pd.DataFrame(part_a_rows).to_csv(
    "results/canonical/part_a_stage4_static.csv", index=False)
print(f"  Saved results/canonical/part_a_stage4_static.csv  ({len(part_a_rows)} rows)\n")

# ---------------------------------------------------------------------------
# Part B — Stage 5 main sweep (3 km × 7 cells × 5 seeds)
# ---------------------------------------------------------------------------

print("=" * 70)
print("Part B — Stage 5 transition dynamics (3 km × 7 cells × 5 seeds)")
print("=" * 70)

part_b_rows = []
agent_snaps = []
total = len(KM_CASES) * len(STAGE5_CELLS) * len(SEEDS)
n = 0
for km in KM_CASES:
    for cell in STAGE5_CELLS:
        for seed in SEEDS:
            n += 1
            print(f"  [{n:3d}/{total}] {km['label']:8s} / "
                  f"{cell['label']:30s}  seed={seed}", flush=True)
            model = make_model(cell, k=km["k"], m=km["m"], seed=seed)
            model.run_model(MAIN_STEPS)
            df = model.datacollector.get_model_vars_dataframe()
            part_b_rows.append(extract_row(df, km["label"], km["k"], km["m"],
                                           cell, seed, "geometric_mean"))

            # Step-300 agent snapshot for Gini decomposition
            adf = model.datacollector.get_agent_vars_dataframe()
            try:
                snap = adf.xs(MAIN_STEPS, level="Step")
            except KeyError:
                last = adf.index.get_level_values("Step").max()
                snap = adf.xs(last, level="Step")
            snap = snap.reset_index()
            snap["km_label"]   = km["label"]
            snap["cell_label"] = cell["label"]
            snap["seed"]       = seed
            agent_snaps.append(
                snap[["km_label", "cell_label", "seed",
                      "AgentID", "AgentType", "Wealth", "Sugar", "Spice"]]
            )

pd.DataFrame(part_b_rows).to_csv(
    "results/canonical/part_b_stage5_main.csv", index=False)
print(f"  Saved results/canonical/part_b_stage5_main.csv  ({len(part_b_rows)} rows)")

pd.concat(agent_snaps, ignore_index=True).to_csv(
    "results/canonical/part_b_agent_step300.csv", index=False)
print(f"  Saved results/canonical/part_b_agent_step300.csv\n")

# ---------------------------------------------------------------------------
# Part C — Welfare sensitivity (LINEAR mode on selected cells)
# ---------------------------------------------------------------------------

print("=" * 70)
print("Part C — Autonomous welfare sensitivity (linear mode)")
print("=" * 70)

part_c_rows = []
total = len(KM_CASES) * len(SENSITIVITY_CELLS) * len(SEEDS)
n = 0
for km in KM_CASES:
    for cell in SENSITIVITY_CELLS:
        for seed in SEEDS:
            n += 1
            print(f"  [{n:3d}/{total}] {km['label']:8s} / "
                  f"{cell['label']:30s}  seed={seed}  [linear]", flush=True)
            model = make_model(cell, k=km["k"], m=km["m"], seed=seed,
                               welfare_mode="linear")
            model.run_model(MAIN_STEPS)
            df = model.datacollector.get_model_vars_dataframe()
            part_c_rows.append(extract_row(df, km["label"], km["k"], km["m"],
                                           cell, seed, "linear"))

pd.DataFrame(part_c_rows).to_csv(
    "results/canonical/part_c_welfare_sensitivity.csv", index=False)
print(f"  Saved results/canonical/part_c_welfare_sensitivity.csv  "
      f"({len(part_c_rows)} rows)\n")

print("Canonical sweep complete.")
