"""Independently reconstruct Table 3 using pairwise absolute wealth differences."""
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np
import pandas as pd

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("snapshot", type=Path)
parser.add_argument("main", type=Path)
parser.add_argument("provenance", choices=["author-deposit", "fresh-replay"])
parser.add_argument("output", type=Path)
args = parser.parse_args()
target_file = Path(__file__).with_name("decomposition-targets.json")
targets = json.loads(target_file.read_text())
labels = {"baseline": "baseline", "labor/UBI": "labour/ubi", "labor/means-tested": "labour/means_tested",
          "wealth/UBI": "wealth/ubi", "wealth/means-tested": "wealth/means_tested",
          "disp-levy/means-tested": "disp_levy/means_tested", "UHI scenario": "uhi_scenario"}
keys = ["km_label", "cell_label", "seed"]
expected = {(speed, cell, seed) for speed in ["slow", "balanced", "fast"] for cell in labels.values() for seed in range(5)}
snapshot = pd.read_csv(args.snapshot)
main = pd.read_csv(args.main)
assert len(main) == 105 and not main.duplicated(keys).any()
assert not snapshot.duplicated([*keys, "AgentID"]).any()
assert set(snapshot[keys].itertuples(index=False, name=None)) == expected
assert set(main[keys].itertuples(index=False, name=None)) == expected
assert set(snapshot.AgentType) == {"HumanAgent", "AIAugmentedAgent", "AutonomousAgent", "OwnerHumanAgent"}
assert np.isfinite(snapshot[["Wealth", "Sugar", "Spice"]].to_numpy()).all()
assert snapshot.Wealth.ge(0).all()
assert np.allclose(snapshot.Wealth, snapshot.Sugar + snapshot.Spice, rtol=1e-10, atol=1e-10)
main = main.set_index(keys)
rows = []
for key, group in snapshot.groupby(keys):
    wealth = group.Wealth.to_numpy(dtype=float)
    n, total_wealth = len(wealth), wealth.sum()
    assert total_wealth > 0
    denominator = 2 * n * total_wealth
    total = np.abs(wealth[:, None] - wealth[None, :]).sum() / denominator
    group_means = group.groupby("AgentType").Wealth.transform("mean").to_numpy()
    between = np.abs(group_means[:, None] - group_means[None, :]).sum() / denominator
    within = 0.0
    for _, subgroup in group.groupby("AgentType"):
        w = subgroup.Wealth.to_numpy(dtype=float)
        within += np.abs(w[:, None] - w[None, :]).sum() / denominator
    residual = total - between - within
    assert 0 <= total <= 1 and residual >= -1e-12
    native = main.loc[key]
    assert n == native.n_working_final + native.n_ai_aug_final + native.n_autonomous_final + native.n_owner_final
    assert np.isclose(total, native.gini_final, rtol=1e-10, atol=1e-10), (key, total, native.gini_final)
    rows.append({"km_label": key[0], "cell_label": key[1], "seed": int(key[2]), "population": n, "total": float(total),
        "between": float(between), "within": float(within), "residual": float(residual),
        "between_percent": float(100 * between / total)})
means = pd.DataFrame(rows).groupby(keys[:2])[["total", "between", "within", "residual", "between_percent"]].mean()
comparison = []
for target in targets["rows"]:
    key = target["speed"], labels[target["cell"]]
    for metric in means.columns:
        value = float(means.loc[key, metric])
        decimals = 0 if metric == "between_percent" else 3
        comparison.append({"speed": key[0], "cell": key[1], "metric": metric, "mean": value,
                           "published": target[metric], "matches": f"{value:.{decimals}f}" == target[metric]})
report = {"provenance": args.provenance, "runs": len(rows), "snapshot_rows": len(snapshot),
          "snapshot_sha256": hashlib.sha256(args.snapshot.read_bytes()).hexdigest(),
          "main_sha256": hashlib.sha256(args.main.read_bytes()).hexdigest(),
          "targets_sha256": hashlib.sha256(target_file.read_bytes()).hexdigest(),
          "method": "Direct pairwise absolute differences; no author analysis functions imported. Between share is averaged per run, not ratio of aggregate means.",
          "per_run": rows, "table_comparison": comparison}
args.output.mkdir(parents=True, exist_ok=False)
(args.output / "table3.json").write_text(json.dumps(report, indent=2, allow_nan=False) + "\n")
print(json.dumps({"runs": len(rows), "table_cells": len(comparison), "matches": sum(r["matches"] for r in comparison)}))
assert all(r["matches"] for r in comparison), "Printed table mismatch; inspect retained report"
