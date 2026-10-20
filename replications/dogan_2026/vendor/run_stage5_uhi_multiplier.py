"""
run_stage5_uhi_multiplier.py — UHI transfer-multiplier sweep (ABM Methods Q3 / check #8).

The paper fixes the UHI per-agent transfer at 2x the balanced means-tested rate.
This sweeps the multiplier over {1, 2, 3, 4} x the means-tested rate across the
three automation speeds and five seeds, to test whether UHI's underperformance
relative to the pure means-tested cells is a knife-edge of the 2x choice or
robust to it. Pure means-tested mortality is included as the comparison benchmark.

Output: results/canonical/uhi_multiplier_sweep.csv
"""
import os
import numpy as np
import pandas as pd
from sugarscape_ai_tax.model import SugarscapeAITax

os.makedirs("results/canonical", exist_ok=True)
SEEDS = list(range(5))
MULTS = [1.0, 2.0, 3.0, 4.0]
KM = [{"label": "slow", "k": 20, "m": 10},
      {"label": "balanced", "k": 10, "m": 10},
      {"label": "fast", "k": 5, "m": 20}]

# thresholds + base means-tested per-agent rate (seed 42), as in run_canonical_sweep.py
_m = SugarscapeAITax(tax_regime="none", redistribution_mode="none", k=0, m=0, seed=42)
_m.run_model(200)
_df = _m.datacollector.get_model_vars_dataframe()
inc = float(_df["MedianIncome"].iloc[199]); wup = 2.0 * float(_df["MedianWealth"].iloc[199])
del _m, _df
_r = SugarscapeAITax(tax_regime="wealth", redistribution_mode="means_tested", k=10, m=10,
                     income_threshold=inc, wealth_threshold_lower=50, wealth_threshold_upper=wup, seed=42)
_r.run_model(300)
_ad = _r.datacollector.get_agent_vars_dataframe()
_el = _ad[_ad["TransferReceived"] > 0]["TransferReceived"]
mt_rate = float(_el.mean()) if len(_el) else 1.0   # base means-tested per-agent rate
del _r, _ad, _el
print(f"base means-tested per-agent rate = {mt_rate:.4f}  (paper uses 2x = {2*mt_rate:.4f})\n")

rows = []
for km in KM:
    # pure means-tested benchmark (wealth/means_tested) for this speed
    for seed in SEEDS:
        for mult in MULTS:
            print(f"  {km['label']:8s} UHI x{mult:.0f} seed={seed}", flush=True)
            m = SugarscapeAITax(tax_regime="uhi_scenario", redistribution_mode="none",
                                k=km["k"], m=km["m"], income_threshold=inc,
                                wealth_threshold_lower=50, wealth_threshold_upper=wup,
                                uhi_transfer_rate=mult * mt_rate, seed=seed)
            m.run_model(300)
            df = m.datacollector.get_model_vars_dataframe()
            rows.append({"km_label": km["label"], "multiplier": mult, "seed": seed,
                         "uhi_rate": mult * mt_rate,
                         "gini_final": float(df["Gini"].iloc[-1]),
                         "deaths": int(df["StarvationDeaths"].sum())})

df = pd.DataFrame(rows)
df.to_csv("results/canonical/uhi_multiplier_sweep.csv", index=False)
print(f"\nSaved results/canonical/uhi_multiplier_sweep.csv ({len(df)} rows)")
# quick benchmark: pure means-tested deaths by km (5-seed mean), from canonical
b = pd.read_csv("results/canonical/part_b_stage5_main.csv")
print("\nUHI deaths by multiplier vs pure means-tested benchmark (5-seed mean):")
for km in ["slow", "balanced", "fast"]:
    mt = b[(b.cell_label == "wealth/means_tested") & (b.km_label == km)].starvation_deaths_total.mean()
    line = f"  {km:8s}  pure-MT={mt:.0f} | "
    for mult in MULTS:
        d = df[(df.km_label == km) & (df.multiplier == mult)].deaths.mean()
        line += f"UHIx{mult:.0f}={d:.0f}  "
    print(line)
