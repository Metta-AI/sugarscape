"""Compare complete native and conserving levy sweeps without dropping seeds."""
import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("original", type=Path, help="Completed original robustness run directory")
parser.add_argument("corrected", type=Path)
parser.add_argument("canonical", type=Path)
parser.add_argument("output", type=Path)
args = parser.parse_args()
records = [json.loads(line) for line in (args.original / "completed.jsonl").read_text().splitlines()]
assert [r for r in records if r["script"] == "run_stage5_D_sweep.py"] == [
    {"script": "run_stage5_D_sweep.py", "exit_code": 0}], "Original 75-run sweep must finish"
for directory in [args.corrected, args.canonical]:
    assert json.loads((directory / "exit.json").read_text())["exit_code"] == 0
original_manifest = json.loads((args.original / "manifest.json").read_text())
corrected_manifest = json.loads((args.corrected / "manifest.json").read_text())
for name, checksum in corrected_manifest["original_sha256"].items():
    if name in original_manifest["source_sha256"]:
        assert checksum == original_manifest["source_sha256"][name]
for name, checksum in corrected_manifest["source_sha256"].items():
    assert hashlib.sha256((args.corrected / "source" / name).read_bytes()).hexdigest() == checksum
assert corrected_manifest["source_sha256"]["sugarscape_ai_tax/model.py"] == "4477a94906cea33d84f05015aa87a2f9b7a68555612e16c9e140e22d3e50e6f2"
assert original_manifest["source_sha256"]["sugarscape_ai_tax/model.py"] == "a3e264cb1640691451b2936cd85a17f21bc8b17f5a2f36977dc8ee1db698ed24"
relative = "results/stage5_D_sweep.csv"
ledger = json.loads((args.corrected / "output-sha256.json").read_text())
assert hashlib.sha256((args.corrected / relative).read_bytes()).hexdigest() == ledger[relative]
keys = ["km_label", "D", "seed"]
expected = {(speed, rate, seed) for speed in ["slow", "balanced", "fast"]
            for rate in [10, 25, 50, 100, 200] for seed in range(5)}
frames = {}
for label, directory in [("original", args.original), ("corrected", args.corrected)]:
    frame = pd.read_csv(directory / relative)
    assert len(frame) == 75 and not frame.duplicated(keys).any()
    assert set(frame[keys].itertuples(index=False, name=None)) == expected
    assert np.isfinite(frame.select_dtypes(include="number").to_numpy()).all()
    assert frame.gini_final.between(0, 1).all()
    assert frame.starvation_deaths_total.gt(0).all() and frame.total_redistribution.gt(0).all()
    assert frame.starvation_deaths_total.eq(frame.deaths_sugar_only + frame.deaths_spice_only + frame.deaths_both).all()
    frames[label] = frame.set_index(keys).sort_index()
assert list(frames["original"].columns) == list(frames["corrected"].columns)
canonical_manifest = json.loads((args.canonical / "manifest.json").read_text())
canonical_path = args.canonical / "results/canonical/part_b_stage5_main.csv"
assert hashlib.sha256(canonical_path.read_bytes()).hexdigest() == canonical_manifest["reference_sha256"]["results/canonical/part_b_stage5_main.csv"]
canonical = pd.read_csv(canonical_path)
canonical = canonical[canonical.cell_label == "disp_levy/means_tested"].set_index(["km_label", "seed"]).sort_index()
original50 = frames["original"].xs(50, level="D")
assert original50.index.equals(canonical.index)
common = [c for c in original50.columns if c in canonical.columns]
assert np.allclose(original50[common], canonical[common], rtol=1e-10, atol=1e-10)
metrics = ["gini_final", "starvation_deaths_total", "total_tax_revenue", "total_redistribution",
           "n_working_final", "n_owner_final", "working_wealth_share_final", "displacements"]
delta = frames["corrected"][metrics] - frames["original"][metrics]
summaries = {}
for label, frame in frames.items():
    means = frame.groupby(level=["km_label", "D"])[metrics].mean()
    by_speed = []
    for speed in ["slow", "balanced", "fast"]:
        group = means.loc[speed]
        values = frame.xs(speed, level="km_label")
        gini_cv = float(group.gini_final.std(ddof=1) / group.gini_final.mean())
        mortality_spread = float(group.starvation_deaths_total.max() / group.starvation_deaths_total.min() - 1)
        share200 = float(100 * group.loc[200, "total_tax_revenue"] / group.loc[200, "total_redistribution"])
        by_speed.append({"speed": speed, "gini_cv_across_D_means": gini_cv, "gini_cv_below_004": gini_cv < .04,
                         "mortality_relative_range": mortality_spread, "mortality_range_below_005": mortality_spread < .05,
                         "working_counts_equal_across_D_each_seed": bool(values.groupby(level="seed").n_working_final.nunique().eq(1).all()),
                         "D200_levy_percent_of_mean_redistribution": share200, "D200_levy_share_below_3percent": share200 < 3})
    summaries[label] = {"means": means.reset_index().to_dict(orient="records"), "claims": by_speed}
report = {"pairs": 75, "canonical_D50_cells_matched": original50[common].size,
          "input_sha256": {label: hashlib.sha256((directory / relative).read_bytes()).hexdigest()
                           for label, directory in [("original", args.original), ("corrected", args.corrected)]},
          "summaries": summaries, "paired_changes": delta.reset_index().to_dict(orient="records"),
          "mean_paired_changes": delta.groupby(level=["km_label", "D"]).mean().reset_index().to_dict(orient="records"),
          "scope": "Declared descriptive sensitivity comparison. Native sweep exports working/owner counts, not complete population or per-step trajectories. No whole-paper verdict."}
args.output.mkdir(parents=True, exist_ok=False)
(args.output / "comparison.json").write_text(json.dumps(report, indent=2, allow_nan=False) + "\n")
print(json.dumps({"pairs": 75, "canonical_cells": report["canonical_D50_cells_matched"],
                  "claims": {label: summary["claims"] for label, summary in summaries.items()}}))
