"""Validate a completed bundled canonical run against the independently replayed author outputs."""
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np
import pandas as pd

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("reference", type=Path, help="Completed original-author canonical replay")
parser.add_argument("fork", type=Path, help="Completed run_fork.py canonical output")
parser.add_argument("output", type=Path)
args = parser.parse_args()
root = Path(__file__).resolve().parent
provenance_bytes = (root / "vendor-provenance.json").read_bytes()
provenance = json.loads(provenance_bytes)
reference = json.loads((args.reference / "manifest.json").read_text())
fork = json.loads((args.fork / "manifest.json").read_text())
assert fork["experiment"] == "canonical", "Requires canonical simulation, not report-only output"
assert reference["revision"] == fork["author_revision"] == provenance["revision"]
assert fork["provenance_sha256"] == hashlib.sha256(provenance_bytes).hexdigest()
assert fork["source_sha256"] == provenance["files_sha256"]
assert fork["environment_sha256"] == hashlib.sha256((root / "environment.txt").read_bytes()).hexdigest()
for name, checksum in provenance["files_sha256"].items():
    assert hashlib.sha256((root / "vendor" / name).read_bytes()).hexdigest() == checksum
for name in ["run_canonical_sweep.py", "sugarscape_ai_tax/model.py", "sugarscape_ai_tax/agents.py",
             "sugarscape_ai_tax/__init__.py", "sugarscape_ai_tax/sugar-map.txt"]:
    assert reference["source_sha256"][name] == fork["source_sha256"][name]
for directory in [args.reference, args.fork]:
    assert json.loads((directory / "exit.json").read_text())["exit_code"] == 0
ledger = json.loads((args.fork / "output-sha256.json").read_text())
expected = [("part_a_stage4_static.csv", 25, 42), ("part_b_stage5_main.csv", 105, 42),
            ("part_b_agent_step300.csv", 24675, 8), ("part_c_welfare_sensitivity.csv", 75, 42)]
assert set(ledger) == {"results/canonical/" + name for name, _, _ in expected}
results = []
for name, rows, columns in expected:
    relative = "results/canonical/" + name
    original_bytes = (args.reference / relative).read_bytes()
    actual_bytes = (args.fork / relative).read_bytes()
    assert hashlib.sha256(original_bytes).hexdigest() == reference["reference_sha256"][relative], "Reference replay differs from pinned deposited data"
    assert hashlib.sha256(actual_bytes).hexdigest() == ledger[relative], "Fork output changed after completion"
    left, right = pd.read_csv(args.reference / relative), pd.read_csv(args.fork / relative)
    assert left.shape == right.shape == (rows, columns)
    assert list(left.columns) == list(right.columns)
    mismatches = []
    for column in left.columns:
        a, b = left[column], right[column]
        if pd.api.types.is_numeric_dtype(a):
            matches = np.isclose(a.to_numpy(dtype=float), b.to_numpy(dtype=float), rtol=1e-10, atol=1e-10, equal_nan=True)
        else:
            matches = (a.eq(b) | (a.isna() & b.isna())).to_numpy()
        mismatches.extend({"row": int(row), "column": column} for row in np.flatnonzero(~matches))
    results.append({"file": name, "rows": rows, "columns": columns, "cells": rows * columns,
        "mismatches": len(mismatches), "first_mismatches": mismatches[:20],
        "reference_sha256": hashlib.sha256(original_bytes).hexdigest(), "fork_sha256": ledger[relative],
        "byte_identical": original_bytes == actual_bytes})
report = {"rtol": 1e-10, "atol": 1e-10, "matching_missing_values_required": True,
          "reference_manifest_sha256": hashlib.sha256((args.reference / "manifest.json").read_bytes()).hexdigest(),
          "fork_manifest_sha256": hashlib.sha256((args.fork / "manifest.json").read_bytes()).hexdigest(),
          "results": results, "scope": "Full205-run canonical execution through bundled original source, not an independent model implementation or complete robustness replication."}
args.output.mkdir(parents=True, exist_ok=False)
(args.output / "comparison.json").write_text(json.dumps(report, indent=2, allow_nan=False) + "\n")
print(json.dumps({"cells": sum(r["cells"] for r in results), "mismatches": sum(r["mismatches"] for r in results),
                  "byte_identical_files": sum(r["byte_identical"] for r in results)}))
assert all(r["mismatches"] == 0 for r in results), "Fork mismatch; inspect retained comparison"
