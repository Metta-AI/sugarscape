"""Compare every canonical output cell against the pinned author data."""
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np
import pandas as pd

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("engine", type=Path)
parser.add_argument("run", type=Path)
parser.add_argument("output", type=Path)
args = parser.parse_args()
assert json.loads((args.run / "exit.json").read_text())["exit_code"] == 0
manifest = json.loads((args.run / "manifest.json").read_text())
args.output.mkdir(parents=True, exist_ok=False)
results = []
for name, expected_rows in [("part_a_stage4_static.csv", 25), ("part_b_stage5_main.csv", 105),
                            ("part_b_agent_step300.csv", 24675), ("part_c_welfare_sensitivity.csv", 75)]:
    relative = "results/canonical/" + name
    source = args.engine / relative
    fresh = args.run / relative
    assert hashlib.sha256(source.read_bytes()).hexdigest() == manifest["reference_sha256"][relative]
    reference = pd.read_csv(source)
    actual = pd.read_csv(fresh)
    assert len(reference) == len(actual) == expected_rows
    assert list(reference.columns) == list(actual.columns)
    mismatches = []
    for column in reference.columns:
        left, right = reference[column], actual[column]
        if pd.api.types.is_numeric_dtype(left):
            matches = np.isclose(left.to_numpy(dtype=float), right.to_numpy(dtype=float),
                                 rtol=1e-10, atol=1e-10, equal_nan=True)
        else:
            matches = (left.eq(right) | (left.isna() & right.isna())).to_numpy()
        mismatches.extend({"row": int(row), "column": column} for row in np.flatnonzero(~matches))
    results.append({"file": name, "rows": len(actual), "columns": len(actual.columns),
                    "cells": actual.size, "mismatches": len(mismatches), "first_mismatches": mismatches[:20],
                    "output_sha256": hashlib.sha256(fresh.read_bytes()).hexdigest()})
report = {"rtol": 1e-10, "atol": 1e-10, "matching_missing_values_required": True,
          "results": results, "scope": "All canonical output cells; this does not validate additional robustness studies or scientific interpretation."}
(args.output / "comparison.json").write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps(report))
assert all(r["mismatches"] == 0 for r in results), "Author-data mismatch; inspect retained comparison"
