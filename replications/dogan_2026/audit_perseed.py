"""Audit the complete native per-seed calibration experiment against canonical results."""
import argparse
import hashlib
import itertools
import json
from pathlib import Path

import numpy as np
import pandas as pd

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("robustness", type=Path)
parser.add_argument("canonical", type=Path)
parser.add_argument("output", type=Path)
args = parser.parse_args()
completed = [json.loads(line) for line in (args.robustness / "completed.jsonl").read_text().splitlines()]
assert [r for r in completed if r["script"] == "run_stage5_perseed_thresholds.py"] == [
    {"script": "run_stage5_perseed_thresholds.py", "exit_code": 0}], "Per-seed calibration sweep is incomplete"
assert json.loads((args.canonical / "exit.json").read_text())["exit_code"] == 0
manifest = json.loads((args.robustness / "manifest.json").read_text())
reference = json.loads((args.canonical / "manifest.json").read_text())
for name in ["sugarscape_ai_tax/model.py", "sugarscape_ai_tax/agents.py", "sugarscape_ai_tax/sugar-map.txt"]:
    assert manifest["source_sha256"][name] == reference["source_sha256"][name]
for name, checksum in manifest["source_sha256"].items():
    assert hashlib.sha256((Path(manifest["engine"]) / name).read_bytes()).hexdigest() == checksum
native_path = args.robustness / "results/stage5_perseed_thresholds.csv"
canonical_path = args.canonical / "results/canonical/part_b_stage5_main.csv"
assert hashlib.sha256(canonical_path.read_bytes()).hexdigest() == reference["reference_sha256"]["results/canonical/part_b_stage5_main.csv"]
keys = ["km_label", "cell_label", "seed"]
cells = ["baseline", "labour/ubi", "labour/means_tested", "wealth/ubi", "wealth/means_tested",
         "disp_levy/means_tested", "uhi_scenario"]
speeds = ["slow", "balanced", "fast"]
expected = set(itertools.product(speeds, cells, range(5)))
frames = {}
for label, path in [("canonical", canonical_path), ("perseed", native_path)]:
    frame = pd.read_csv(path)
    assert len(frame) == 105 and not frame.duplicated(keys).any()
    assert set(frame[keys].itertuples(index=False, name=None)) == expected
    assert np.isfinite(frame.select_dtypes(include="number").to_numpy()).all()
    assert frame.gini_final.between(0, 1).all()
    assert frame.starvation_deaths_total.eq(frame.deaths_sugar_only + frame.deaths_spice_only + frame.deaths_both).all()
    frames[label] = frame.set_index(keys).sort_index()
thresholds = ["income_threshold_used", "wealth_upper_used", "uhi_transfer_rate_used"]
assert frames["perseed"].groupby(level="seed")[thresholds].nunique().eq(1).all().all()
assert frames["perseed"][thresholds].gt(0).all().all()
metrics = ["gini_final", "starvation_deaths_total"]
means = {label: frame.groupby(level=keys[:2])[metrics].mean() for label, frame in frames.items()}
changes = means["perseed"] - means["canonical"]
rank_checks = []
for metric in metrics:
    for speed in speeds:
        before = means["canonical"].loc[speed, metric]
        after = means["perseed"].loc[speed, metric]
        changed = []
        ties = []
        for left, right in itertools.combinations(cells, 2):
            a, b = float(before[left] - before[right]), float(after[left] - after[right])
            if a == 0 or b == 0:
                ties.append([left, right])
            if np.sign(a) != np.sign(b):
                changed.append({"cells": [left, right], "canonical_gap": abs(a), "perseed_gap": abs(b),
                                "strict_reversal": bool(a * b < 0)})
        order = list(before.sort_values().index)
        rank_checks.append({"metric": metric, "speed": speed, "canonical_order": order,
                            "perseed_order": list(after.sort_values().index), "ties": ties, "changed_pairs": changed,
                            "one_adjacent_strict_swap": bool(len(changed) == 1 and changed[0]["strict_reversal"] and
                                abs(order.index(changed[0]["cells"][0]) - order.index(changed[0]["cells"][1])) == 1)})
maximum = float(changes.gini_final.abs().max())
report = {"runs": 105, "input_sha256": {"perseed": hashlib.sha256(native_path.read_bytes()).hexdigest(),
          "canonical": hashlib.sha256(canonical_path.read_bytes()).hexdigest()},
          "thresholds": frames["perseed"].groupby(level="seed")[thresholds].first().reset_index().to_dict(orient="records"),
          "rank_checks": rank_checks, "maximum_absolute_change_in_cell_mean_gini": maximum,
          "matches_printed_0022_at_three_decimals": f"{maximum:.3f}" == "0.022",
          "mean_changes": changes.reset_index().to_dict(orient="records"),
          "paired_seed_changes": (frames["perseed"][metrics] - frames["canonical"][metrics]).reset_index().to_dict(orient="records"),
          "scope": "Descriptive means and pairwise ranking audit of manuscript section 4.3. No deposited per-seed-threshold CSV exists; not an exact author-data comparison or significance test."}
args.output.mkdir(parents=True, exist_ok=False)
(args.output / "audit.json").write_text(json.dumps(report, indent=2, allow_nan=False) + "\n")
print(json.dumps({"maximum_mean_gini_change": maximum, "rank_checks": rank_checks}))
