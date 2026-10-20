"""
analyze_canonical.py — produce all paper tables (1–7) plus welfare-sensitivity
report from the canonical-sweep CSVs.  All tables drawn from the SAME model
version (post-torus, current instrumentation), so no mixed-vintage numbers.

Inputs (under results/canonical/):
  part_a_stage4_static.csv
  part_b_stage5_main.csv
  part_b_agent_step300.csv
  part_c_welfare_sensitivity.csv

Outputs (under results/canonical/):
  table_1_static_composition.txt    — Stage 4 cells, Gini + deaths
  table_2_gini_by_cell_km.txt       — 21 cells × Gini@end, 5-seed mean ± CV
  table_3_deaths_by_cell_km.txt     — 21 cells × starvation, 5-seed mean ± CV
  table_4_seed_robustness.txt       — CV across seeds for deaths/Gini
  table_5_wealth_at_death.txt       — mean wealth at starvation, per-resource split
  table_6_wealth_at_death_seeds.txt — per-seed wealth at death (replaces draft Table 6)
  table_7_uhi_alongside.txt         — UHI scenario alongside 2×2 means-tested
  welfare_sensitivity_report.txt    — geometric vs linear mode comparison
  internal_consistency_check.txt    — cross-CSV invariant checks
"""

import os
import numpy as np
import pandas as pd

DIR = "results/canonical"
os.makedirs(DIR, exist_ok=True)

a = pd.read_csv(f"{DIR}/part_a_stage4_static.csv")
b = pd.read_csv(f"{DIR}/part_b_stage5_main.csv")
c = pd.read_csv(f"{DIR}/part_c_welfare_sensitivity.csv")
snap = pd.read_csv(f"{DIR}/part_b_agent_step300.csv")

CELL_ORDER_STAGE4 = ["baseline", "labour/ubi", "labour/means_tested",
                     "wealth/ubi", "wealth/means_tested"]
CELL_ORDER_STAGE5 = CELL_ORDER_STAGE4 + ["disp_levy/means_tested", "uhi_scenario"]
KM_ORDER = ["slow", "balanced", "fast"]


def _mean_std_cv(series):
    m  = float(series.mean())
    sd = float(series.std(ddof=1)) if len(series) > 1 else float("nan")
    cv = sd / m if m else float("nan")
    return m, sd, cv


# =============================================================================
# Table 1 — Stage 4 static composition
# =============================================================================

lines = [
    "Table 1. Policy comparison under static composition (k=0, m=0).",
    "Mean over 5 seeds (s=0..4); CV across seeds in parens.",
    "",
    f"{'Cell':30s}  {'Gini@300':>14s}  {'StarvDeaths':>16s}",
    "-" * 66,
]
for cell in CELL_ORDER_STAGE4:
    sub = a[a["cell_label"] == cell]
    gm, gs, gv = _mean_std_cv(sub["gini_final"])
    dm, ds, dv = _mean_std_cv(sub["starvation_deaths_total"])
    lines.append(
        f"{cell:30s}  {gm:6.4f} (cv {gv:5.3f})  "
        f"{dm:7.1f} (cv {dv:5.3f})"
    )
with open(f"{DIR}/table_1_static_composition.txt", "w") as f:
    f.write("\n".join(lines) + "\n")
print("[T1] Saved table_1_static_composition.txt")


# =============================================================================
# Table 2 — Gini by cell × km
# =============================================================================

lines = [
    "Table 2. Gini coefficient at step 300, 21 (cell × km) combinations.",
    "Mean over 5 seeds; CV across seeds in parens.",
    "",
    f"{'Cell':30s}  " + "  ".join(f"{km:>15s}" for km in KM_ORDER),
    "-" * 84,
]
for cell in CELL_ORDER_STAGE5:
    parts = [f"{cell:30s}"]
    for km in KM_ORDER:
        sub = b[(b["cell_label"] == cell) & (b["km_label"] == km)]
        m, s, v = _mean_std_cv(sub["gini_final"])
        parts.append(f"{m:6.4f} (cv {v:5.3f})")
    lines.append("  " + "  ".join(parts).strip())
with open(f"{DIR}/table_2_gini_by_cell_km.txt", "w") as f:
    f.write("\n".join(lines) + "\n")
print("[T2] Saved table_2_gini_by_cell_km.txt")


# =============================================================================
# Table 3 — Starvation deaths by cell × km
# =============================================================================

lines = [
    "Table 3. Cumulative starvation deaths over 300 steps, 21 combinations.",
    "Mean over 5 seeds; CV across seeds in parens.",
    "",
    f"{'Cell':30s}  " + "  ".join(f"{km:>16s}" for km in KM_ORDER),
    "-" * 88,
]
for cell in CELL_ORDER_STAGE5:
    parts = [f"{cell:30s}"]
    for km in KM_ORDER:
        sub = b[(b["cell_label"] == cell) & (b["km_label"] == km)]
        m, s, v = _mean_std_cv(sub["starvation_deaths_total"])
        parts.append(f"{m:7.1f} (cv {v:5.3f})")
    lines.append("  " + "  ".join(parts).strip())
with open(f"{DIR}/table_3_deaths_by_cell_km.txt", "w") as f:
    f.write("\n".join(lines) + "\n")
print("[T3] Saved table_3_deaths_by_cell_km.txt")


# =============================================================================
# Table 4 — Seed robustness (CV for deaths)
# =============================================================================

lines = [
    "Table 4. Seed robustness — CV across 5 seeds for cumulative starvation",
    "deaths.  CV < 0.15 is the conventional ABM threshold for robust findings.",
    "",
    f"{'Cell':30s}  " + "  ".join(f"{km:>14s}" for km in KM_ORDER),
    "-" * 78,
]
for cell in CELL_ORDER_STAGE5:
    parts = [f"{cell:30s}"]
    for km in KM_ORDER:
        sub = b[(b["cell_label"] == cell) & (b["km_label"] == km)]
        m, s, v = _mean_std_cv(sub["starvation_deaths_total"])
        flag = "  " if v < 0.15 else "**"  # ** flags above-threshold CVs
        parts.append(f"{m:6.1f} cv={v:5.3f}{flag}")
    lines.append("  " + "  ".join(parts).strip())
lines.append("")
lines.append("** = CV above the 0.15 conventional ABM threshold.")
with open(f"{DIR}/table_4_seed_robustness.txt", "w") as f:
    f.write("\n".join(lines) + "\n")
print("[T4] Saved table_4_seed_robustness.txt")


# =============================================================================
# Table 5 — Mean wealth at starvation death + per-resource split
# =============================================================================

lines = [
    "Table 5. Mean wealth at starvation death, 21 combinations.",
    "Mean over 5 seeds; values are weighted by deaths per step.",
    "Columns: Total | Sugar | Spice | %SR (single-resource collapse fraction).",
    "",
]
for km in KM_ORDER:
    lines.append(f"-- {km} --")
    lines.append(
        f"{'Cell':30s}  {'Total':>7}  {'Sugar':>7}  {'Spice':>7}  {'%SR':>5}"
    )
    lines.append("-" * 64)
    for cell in CELL_ORDER_STAGE5:
        sub = b[(b["cell_label"] == cell) & (b["km_label"] == km)]
        wm = float(sub["mean_wealth_at_death"].mean())
        sm = float(sub["mean_sugar_at_death"].mean())
        pm = float(sub["mean_spice_at_death"].mean())
        srf = float(((sub["deaths_sugar_only"] + sub["deaths_spice_only"]) /
                     sub["starvation_deaths_total"].clip(lower=1)).mean()) * 100
        lines.append(
            f"{cell:30s}  {wm:7.2f}  {sm:7.2f}  {pm:7.2f}  {srf:4.1f}%"
        )
    lines.append("")
with open(f"{DIR}/table_5_wealth_at_death.txt", "w") as f:
    f.write("\n".join(lines) + "\n")
print("[T5] Saved table_5_wealth_at_death.txt")


# =============================================================================
# Table 6 — Per-seed wealth at death (replaces draft Table 6)
# =============================================================================

lines = [
    "Table 6. Mean wealth at starvation death, per seed (5 seeds).",
    "Replaces the draft's seed=42 column with the full per-seed picture.",
    "",
    f"{'KM':10s}  {'Cell':30s}  " + "  ".join(f"s={s:>1}" for s in range(5))
    + f"   {'mean':>5}",
    "-" * 80,
]
for km in KM_ORDER:
    for cell in CELL_ORDER_STAGE5:
        sub = b[(b["cell_label"] == cell) & (b["km_label"] == km)].sort_values("seed")
        seedvals = sub["mean_wealth_at_death"].tolist()
        m = float(np.nanmean(seedvals))
        parts = "  ".join(f"{v:5.1f}" for v in seedvals)
        lines.append(f"{km:10s}  {cell:30s}  {parts}   {m:5.1f}")
    lines.append("")
with open(f"{DIR}/table_6_wealth_at_death_seeds.txt", "w") as f:
    f.write("\n".join(lines) + "\n")
print("[T6] Saved table_6_wealth_at_death_seeds.txt")


# =============================================================================
# Table 7 — UHI alongside 2×2 means-tested cells
# =============================================================================

T7_CELLS = ["labour/means_tested", "wealth/means_tested",
            "disp_levy/means_tested", "uhi_scenario"]

lines = [
    "Table 7. UHI scenario alongside the 2×2 means-tested matrix.",
    "Mean over 5 seeds.",
    "",
    f"{'KM':10s}  {'Cell':30s}  {'Gini':>7s}  {'Deaths':>7s}",
    "-" * 60,
]
for km in KM_ORDER:
    for cell in T7_CELLS:
        sub = b[(b["cell_label"] == cell) & (b["km_label"] == km)]
        g = float(sub["gini_final"].mean())
        d = float(sub["starvation_deaths_total"].mean())
        lines.append(f"{km:10s}  {cell:30s}  {g:6.4f}  {d:7.1f}")
    lines.append("")
with open(f"{DIR}/table_7_uhi_alongside.txt", "w") as f:
    f.write("\n".join(lines) + "\n")
print("[T7] Saved table_7_uhi_alongside.txt")


# =============================================================================
# Welfare-sensitivity report (Part C vs Part B, matched cells/km/seeds)
# =============================================================================

SENS_CELLS = ["baseline", "labour/means_tested", "wealth/means_tested",
              "disp_levy/means_tested", "uhi_scenario"]

lines = [
    "Welfare-sensitivity report — autonomous welfare function: geometric_mean vs linear.",
    "Cells: baseline + 4 means-tested cells; 3 km × 5 seeds each.",
    "",
    "(geom) = current paper default; (lin) = sensitivity check.",
    "",
    f"{'KM':10s}  {'Cell':30s}  "
    f"{'G_geom':>7}  {'G_lin':>7}  {'ΔG':>7}  "
    f"{'D_geom':>7}  {'D_lin':>7}  {'ΔD%':>6}  "
    f"{'T_MA_geom':>9}  {'T_MA_lin':>9}",
    "-" * 116,
]
for km in KM_ORDER:
    for cell in SENS_CELLS:
        bg = b[(b["cell_label"] == cell) & (b["km_label"] == km)]
        cl = c[(c["cell_label"] == cell) & (c["km_label"] == km)]
        g_geom = float(bg["gini_final"].mean())
        g_lin  = float(cl["gini_final"].mean())
        d_geom = float(bg["starvation_deaths_total"].mean())
        d_lin  = float(cl["starvation_deaths_total"].mean())
        tma_geom = float(bg["trade_exchanges_mortal_auto"].mean())
        tma_lin  = float(cl["trade_exchanges_mortal_auto"].mean())
        d_pct = 100.0 * (d_lin - d_geom) / d_geom if d_geom else float("nan")
        lines.append(
            f"{km:10s}  {cell:30s}  "
            f"{g_geom:6.4f}  {g_lin:6.4f}  {g_lin-g_geom:+7.4f}  "
            f"{d_geom:7.1f}  {d_lin:7.1f}  {d_pct:+5.1f}%  "
            f"{tma_geom:9.0f}  {tma_lin:9.0f}"
        )
    lines.append("")

lines += [
    "Reading:",
    "  ΔG  — change in Gini@300 when switching to linear welfare.  Small (<0.02)",
    "        means the rankings the paper depends on don't move.",
    "  ΔD% — change in cumulative starvation deaths.  If small, the linear-welfare",
    "        autonomous offers a similar survival channel to the geometric mode.",
    "  T_MA — trade exchanges between mortal and autonomous agents (cumulative).",
    "        Larger gap between geom and lin = welfare-function choice substantially",
    "        affects how often the cross-type trade fires.",
    "",
    "If ΔG < 0.02 and ΔD% < 10% across the table, the qualitative paper findings",
    "are robust to the autonomous-welfare-function choice.  In that case the",
    "welfare-function decision is a methodological point worth flagging in §2.4",
    "but does not threaten any headline claim.",
]

with open(f"{DIR}/welfare_sensitivity_report.txt", "w") as f:
    f.write("\n".join(lines) + "\n")
print("[WSR] Saved welfare_sensitivity_report.txt")


# =============================================================================
# Internal-consistency check
# =============================================================================

cks = []
cks.append(f"Part A rows: {len(a)} (expect 25)")
cks.append(f"Part B rows: {len(b)} (expect 105)")
cks.append(f"Part C rows: {len(c)} (expect 75)")
cks.append(f"Snapshot rows: {len(snap)}")
# All A rows should have welfare_mode == geometric_mean
cks.append(f"Part A welfare modes: {sorted(a['welfare_mode'].unique())}")
cks.append(f"Part B welfare modes: {sorted(b['welfare_mode'].unique())}")
cks.append(f"Part C welfare modes: {sorted(c['welfare_mode'].unique())}")

# Invariant: deaths_sugar_only + deaths_spice_only + deaths_both == starvation_deaths_total
for name, df in [("Part A", a), ("Part B", b), ("Part C", c)]:
    delta = (df["starvation_deaths_total"]
             - df["deaths_sugar_only"]
             - df["deaths_spice_only"]
             - df["deaths_both"])
    n_bad = int((delta.abs() > 0).sum())
    cks.append(f"{name}: per-resource death sum check — "
               f"{n_bad} rows mismatched (expect 0)")

with open(f"{DIR}/internal_consistency_check.txt", "w") as f:
    f.write("\n".join(cks) + "\n")
print("[CK] Saved internal_consistency_check.txt")

print("\nAll tables written under", DIR)
