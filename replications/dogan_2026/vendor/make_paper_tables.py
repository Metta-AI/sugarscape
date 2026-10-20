"""
make_paper_tables.py — emit all paper tables as markdown, numbered to match the
SYNCED draft's [TABLE N] markers, sourced entirely from results/canonical/.

Draft numbering (from the synced draft's section text):
  T1 §3.2  static composition: Gini + deaths, 5 cells           (part_a)
  T2 §4.1  Gini @300, 21 combos, 5-seed mean (+CV)              (part_b)
  T3 §4.2  Pyatt decomposition @300                             (part_b_agent_step300)
  T4 §4.3  cumulative deaths, 21 combos, 5-seed mean + CV       (part_b)
  T5 §4.4  per-resource cause of death + stock split           (part_b)
  T6 §5.2  UHI alongside 2x2 + levy: Gini + deaths             (part_b)
  B.1 App B welfare sensitivity: geom vs linear                (part_b vs part_c)
  C.1 App C composition sensitivity                            (part_b vs composition_sweep)

Output: results/canonical/paper_tables.md
"""

import numpy as np
import pandas as pd

DIR = "results/canonical"
a = pd.read_csv(f"{DIR}/part_a_stage4_static.csv")
b = pd.read_csv(f"{DIR}/part_b_stage5_main.csv")
c = pd.read_csv(f"{DIR}/part_c_welfare_sensitivity.csv")
snap = pd.read_csv(f"{DIR}/part_b_agent_step300.csv")
comp = pd.read_csv(f"{DIR}/composition_sweep.csv")

KM = ["slow", "balanced", "fast"]
CELL5 = ["baseline", "labour/ubi", "labour/means_tested", "wealth/ubi", "wealth/means_tested"]
CELL7 = CELL5 + ["disp_levy/means_tested", "uhi_scenario"]
# CSV cell_label (UK-spelled identifier) -> US-spelling display label for the paper.
DISP = {
    "baseline": "baseline",
    "labour/ubi": "labor/UBI",
    "labour/means_tested": "labor/means-tested",
    "wealth/ubi": "wealth/UBI",
    "wealth/means_tested": "wealth/means-tested",
    "disp_levy/means_tested": "disp-levy/means-tested",
    "uhi_scenario": "UHI scenario",
}


def msc(s):
    m = float(s.mean()); sd = float(s.std(ddof=1)) if len(s) > 1 else 0.0
    return m, (sd / m if m else 0.0)


def gini(w):
    w = np.sort(np.clip(np.asarray(w, float), 0, None)); n = len(w); t = w.sum()
    if n == 0 or t == 0: return 0.0
    return float(np.sum((2 * np.arange(1, n + 1) - n - 1) * w) / (n * t))


out = []

# ---------------- Table 1 ----------------
out.append("### Table 1. Static composition (k = m = 0): Gini and mortality (5-seed means; CV in parentheses).\n")
out.append("| Policy cell | Gini @300 | Deaths from resource exhaustion |")
out.append("|---|---|---|")
for cell in CELL5:
    s = a[a.cell_label == cell]
    g, gcv = msc(s.gini_final); d, dcv = msc(s.starvation_deaths_total)
    out.append(f"| {DISP[cell]} | {g:.3f} ({gcv:.3f}) | {d:.1f} ({dcv:.3f}) |")
out.append("")

# ---------------- Table 2 ----------------
out.append("### Table 2. Gini coefficient at step 300 across 21 (policy × automation speed) combinations (5-seed means; CV in parentheses).\n")
out.append("| Policy cell | Slow (k=20,m=10) | Balanced (k=10,m=10) | Fast (k=5,m=20) |")
out.append("|---|---|---|---|")
for cell in CELL7:
    row = [f"| {DISP[cell]} "]
    for km in KM:
        g, gcv = msc(b[(b.cell_label == cell) & (b.km_label == km)].gini_final)
        row.append(f"| {g:.3f} ({gcv:.3f}) ")
    out.append("".join(row) + "|")
out.append("")

# ---------------- Table 3 (Pyatt) ----------------
TYPES = ["HumanAgent", "AIAugmentedAgent", "AutonomousAgent", "OwnerHumanAgent"]
def pyatt(wbt):
    allw = np.concatenate(list(wbt.values())); G = gini(allw)
    N = len(allw); T = allw.sum()
    if T == 0: return G, 0, 0, 0
    mvec = np.empty(N); i = 0; within = 0.0
    for k, w in wbt.items():
        nk = len(w); pk = nk / N; sk = w.sum() / T; gk = gini(w)
        within += sk * pk * gk; mvec[i:i+nk] = (w.mean() if nk else 0); i += nk
    GB = gini(mvec); R = G - GB - within
    return G, GB, within, R

out.append("### Table 3. Pyatt decomposition of the step-300 Gini by agent type (5-seed means). G = G_B + Σ s·p·G_k + R.\n")
out.append("| Policy cell | Speed | G total | G between | within Σspg | residual R | between share |")
out.append("|---|---|---|---|---|---|---|")
for cell in CELL7:
    for km in KM:
        rows = []
        for seed, sub in snap[(snap.cell_label == cell) & (snap.km_label == km)].groupby("seed"):
            wbt = {t: sub[sub.AgentType == t].Wealth.values for t in TYPES}
            wbt = {k: v for k, v in wbt.items() if len(v)}
            rows.append(pyatt(wbt))
        G, GB, W, R = np.mean(rows, axis=0)
        out.append(f"| {DISP[cell]} | {km} | {G:.3f} | {GB:.3f} | {W:.3f} | {R:.3f} | {100*GB/G:.0f}% |")
out.append("")

# ---------------- Table 4 (deaths: 5-seed mean + CV) ----------------
out.append("### Table 4. Cumulative deaths from resource exhaustion over 300 steps, 21 combinations: 5-seed means with coefficient of variation (CV < 0.15 = conventional ABM threshold).\n")
out.append("| Policy cell | Slow mean (CV) | Balanced mean (CV) | Fast mean (CV) |")
out.append("|---|---|---|---|")
for cell in CELL7:
    row = [f"| {DISP[cell]} "]
    for km in KM:
        d, dcv = msc(b[(b.cell_label == cell) & (b.km_label == km)].starvation_deaths_total)
        row.append(f"| {d:.1f} ({dcv:.3f}) ")
    out.append("".join(row) + "|")
out.append("")

# ---------------- Table 5 (per-resource) ----------------
out.append("### Table 5. Structure of mortality: single-resource vs joint collapse, and mean surviving-resource stock at death (5-seed means).\n")
out.append("| Policy cell | Speed | Deaths | Sugar-only | Spice-only | Joint | % single-resource | Stock at death |")
out.append("|---|---|---|---|---|---|---|---|")
for cell in CELL7:
    for km in KM:
        s = b[(b.cell_label == cell) & (b.km_label == km)]
        tot = s.starvation_deaths_total.mean()
        so = s.deaths_sugar_only.mean(); sp = s.deaths_spice_only.mean(); jo = s.deaths_both.mean()
        srf = 100 * ((s.deaths_sugar_only + s.deaths_spice_only) / s.starvation_deaths_total.clip(lower=1)).mean()
        stock = s.mean_wealth_at_death.mean()
        out.append(f"| {DISP[cell]} | {km} | {tot:.1f} | {so:.1f} | {sp:.1f} | {jo:.1f} | {srf:.1f}% | {stock:.1f} |")
out.append("")

# ---------------- Table 6 (UHI alongside) ----------------
T7 = ["labour/means_tested", "wealth/means_tested", "disp_levy/means_tested", "uhi_scenario"]
out.append("### Table 6. Universal High Income alongside the means-tested cells and displacement levy (5-seed means).\n")
out.append("| Policy cell | Speed | Gini @300 | Deaths | Deaths (% of baseline) |")
out.append("|---|---|---|---|---|")
for km in KM:
    base = float(b[(b.cell_label == "baseline") & (b.km_label == km)].starvation_deaths_total.mean())
    for cell in T7:
        s = b[(b.cell_label == cell) & (b.km_label == km)]
        g = float(s.gini_final.mean()); d = float(s.starvation_deaths_total.mean())
        out.append(f"| {DISP[cell]} | {km} | {g:.3f} | {d:.1f} | {100*d/base:.1f}% |")
out.append("")

# ---------------- Table B.1 (welfare sensitivity) ----------------
SENS = ["baseline", "labour/means_tested", "wealth/means_tested", "disp_levy/means_tested", "uhi_scenario"]
out.append("### Table B.1. Autonomous-agent welfare specification: geometric-mean (default) vs linear. 5-seed means.\n")
out.append("| Policy cell | Speed | Gini geom | Gini linear | ΔGini | Deaths geom | Deaths linear | ΔDeaths % | Mortal↔auto trades (geom / linear) |")
out.append("|---|---|---|---|---|---|---|---|---|")
for km in KM:
    for cell in SENS:
        bg = b[(b.cell_label == cell) & (b.km_label == km)]
        cl = c[(c.cell_label == cell) & (c.km_label == km)]
        gg = bg.gini_final.mean(); gl = cl.gini_final.mean()
        dg = bg.starvation_deaths_total.mean(); dl = cl.starvation_deaths_total.mean()
        tg = bg.trade_exchanges_mortal_auto.mean(); tl = cl.trade_exchanges_mortal_auto.mean()
        dpct = 100 * (dl - dg) / dg if dg else float("nan")
        out.append(f"| {DISP[cell]} | {km} | {gg:.3f} | {gl:.3f} | {gl-gg:+.3f} | {dg:.1f} | {dl:.1f} | {dpct:+.1f}% | {tg:.0f} / {tl:.0f} |")
out.append("")

# ---------------- Table C.1 (composition sensitivity) ----------------
out.append("### Table C.1. Initial-composition sensitivity. Gini and deaths under low (160/20/10/10), baseline (120/40/20/20), and high (80/60/30/30) initial automation. 5-seed means.\n")
out.append("| Policy cell | Speed | Gini low | Gini base | Gini high | Deaths low | Deaths base | Deaths high |")
out.append("|---|---|---|---|---|---|---|---|")
cbase = b.assign(composition="baseline")
callc = pd.concat([cbase[["composition","km_label","cell_label","seed","gini_final","starvation_deaths_total"]],
                   comp[["composition","km_label","cell_label","seed","gini_final","starvation_deaths_total"]]],
                  ignore_index=True)
for cell in CELL7:
    for km in KM:
        def gv(co, col):
            s = callc[(callc.composition==co)&(callc.cell_label==cell)&(callc.km_label==km)][col]
            return float(s.mean()) if len(s) else float("nan")
        out.append(f"| {DISP[cell]} | {km} | {gv('low','gini_final'):.3f} | {gv('baseline','gini_final'):.3f} | "
                   f"{gv('high','gini_final'):.3f} | {gv('low','starvation_deaths_total'):.1f} | "
                   f"{gv('baseline','starvation_deaths_total'):.1f} | {gv('high','starvation_deaths_total'):.1f} |")
out.append("")

with open(f"{DIR}/paper_tables.md", "w") as f:
    f.write("\n".join(out) + "\n")
print(f"Wrote {DIR}/paper_tables.md ({len(out)} lines)")
