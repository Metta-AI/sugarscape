"""Compare a completed original robustness experiment with its pinned deposit."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import numpy as np
import pandas as pd

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("engine", type=Path)
parser.add_argument("run", type=Path)
parser.add_argument("experiment", choices=["horizon", "composition", "uhi"])
parser.add_argument("output", type=Path)
args = parser.parse_args()
experiments = {
    "horizon": ("run_stage5_horizon.py", "horizon_sweep.csv", 45, ["km_label", "cell_label", "seed"]),
    "composition": ("run_composition_sweep.py", "composition_sweep.csv", 210, ["composition", "km_label", "cell_label", "seed"]),
    "uhi": ("run_stage5_uhi_multiplier.py", "uhi_multiplier_sweep.csv", 60, ["km_label", "multiplier", "seed"]),
}
script, filename, expected_rows, keys = experiments[args.experiment]
revision = "0b6a3df470388f60535d8ffb67c34a7f9fa0059a"
assert subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=args.engine, text=True).strip() == revision
manifest = json.loads((args.run / "manifest.json").read_text())
for name, checksum in manifest["source_sha256"].items():
    assert hashlib.sha256((args.engine / name).read_bytes()).hexdigest() == checksum
assert script in manifest["source_sha256"]
if args.experiment == "uhi":
    assert json.loads((args.run / "exit.json").read_text())["exit_code"] == 0
    assert hashlib.sha256((args.run / "results/canonical/part_b_stage5_main.csv").read_bytes()).hexdigest() == manifest["benchmark_sha256"]
else:
    completed = [json.loads(line) for line in (args.run / "completed.jsonl").read_text().splitlines()]
    selected = [r for r in completed if r["script"] == script]
    assert len(selected) == 1 and selected[0]["exit_code"] == 0
relative = "results/canonical/" + filename
reference_bytes = subprocess.check_output(["git", "show", f"{revision}:{relative}"], cwd=args.engine)
assert (args.engine / relative).read_bytes() == reference_bytes
reference = pd.read_csv(args.engine / relative)
fresh = pd.read_csv(args.run / relative)
assert len(reference) == len(fresh) == expected_rows
assert list(reference.columns) == list(fresh.columns)
assert not reference.duplicated(keys).any() and not fresh.duplicated(keys).any()
assert set(reference[keys].itertuples(index=False, name=None)) == set(fresh[keys].itertuples(index=False, name=None))
# Compare every cell in native order, including identifiers and missingness.
mismatches = []
for column in reference.columns:
    left, right = reference[column], fresh[column]
    if pd.api.types.is_numeric_dtype(left):
        matches = np.isclose(left.to_numpy(dtype=float), right.to_numpy(dtype=float), rtol=1e-10, atol=1e-10, equal_nan=True)
    else:
        matches = (left.eq(right) | (left.isna() & right.isna())).to_numpy()
    mismatches.extend({"row": int(row), "column": column} for row in np.flatnonzero(~matches))
report = {"experiment": args.experiment, "revision": revision, "rows": len(fresh), "columns": len(fresh.columns),
          "cells": fresh.size, "mismatches": len(mismatches), "first_mismatches": mismatches[:20],
          "rtol": 1e-10, "atol": 1e-10, "matching_missing_values_required": True,
          "source_manifest_sha256": hashlib.sha256((args.run / "manifest.json").read_bytes()).hexdigest(),
          "reference_sha256": hashlib.sha256(reference_bytes).hexdigest(),
          "fresh_sha256": hashlib.sha256((args.run / relative).read_bytes()).hexdigest(),
          "byte_identical": (args.run / relative).read_bytes() == reference_bytes,
          "scope": "Complete native experiment output comparison; manuscript interpretation requires separate checks."}
args.output.mkdir(parents=True, exist_ok=False)
(args.output / "comparison.json").write_text(json.dumps(report, indent=2, allow_nan=False) + "\n")
print(json.dumps(report))
assert not mismatches, "Author-data mismatch; inspect retained comparison"
