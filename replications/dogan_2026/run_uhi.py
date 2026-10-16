"""Replay the author transfer-multiplier sweep with fresh canonical benchmarks."""
import argparse
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import platform
import subprocess
import sys

import numpy as np
import pandas as pd

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("engine", type=Path)
parser.add_argument("canonical", type=Path)
parser.add_argument("output", type=Path)
args = parser.parse_args()
engine = args.engine.resolve()
root = Path(__file__).resolve().parent
assert subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=engine, text=True).strip() == "0b6a3df470388f60535d8ffb67c34a7f9fa0059a"
assert not subprocess.check_output(["git", "status", "--porcelain", "--untracked-files=no"], cwd=engine, text=True).strip()
assert platform.python_version() == "3.12.4"
for line in (root / "environment.txt").read_text().splitlines():
    name, version = line.split("==")
    assert importlib.metadata.version(name) == version
canonical_manifest = json.loads((args.canonical / "manifest.json").read_text())
relative = "results/canonical/part_b_stage5_main.csv"
reference_bytes = (engine / relative).read_bytes()
assert hashlib.sha256(reference_bytes).hexdigest() == canonical_manifest["reference_sha256"][relative]
benchmark_bytes = (args.canonical / relative).read_bytes()
reference = pd.read_csv(engine / relative)
benchmark = pd.read_csv(args.canonical / relative)
assert len(reference) == len(benchmark) == 105
assert list(reference.columns) == list(benchmark.columns)
for column in reference.columns:
    left, right = reference[column], benchmark[column]
    if pd.api.types.is_numeric_dtype(left):
        assert np.isclose(left.to_numpy(dtype=float), right.to_numpy(dtype=float), rtol=1e-10, atol=1e-10, equal_nan=True).all(), column
    else:
        assert (left.eq(right) | (left.isna() & right.isna())).all(), column
files = [*sorted((engine / "sugarscape_ai_tax").glob("*.py")), engine / "sugarscape_ai_tax/sugar-map.txt",
         engine / "run_stage5_uhi_multiplier.py"]
checksums = {str(p.relative_to(engine)): hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
args.output.mkdir(parents=True, exist_ok=False)
output = args.output.resolve()
(output / "results/canonical").mkdir(parents=True)
(output / relative).write_bytes(benchmark_bytes)
manifest = {"engine": str(engine), "python": sys.version, "source_sha256": checksums,
    "benchmark_source": str(args.canonical.resolve() / relative),
    "benchmark_sha256": hashlib.sha256(benchmark_bytes).hexdigest(),
    "benchmark_validation": "All105rows and all columns match author deposit at rtol=atol=1e-10, including missingness",
    "environment_lock_sha256": hashlib.sha256((root / "environment.txt").read_bytes()).hexdigest(),
    "reference_output_sha256": hashlib.sha256((engine / "results/canonical/uhi_multiplier_sweep.csv").read_bytes()).hexdigest(),
    "protocol": {"seeds": list(range(5)), "multipliers": [1, 2, 3, 4], "speeds": ["slow", "balanced", "fast"],
                 "runs": 60, "horizon": 300, "calibration_runs": 2}}
(output / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
with (output / "native.log").open("x") as log:
    result = subprocess.run([sys.executable, "-u", str(engine / "run_stage5_uhi_multiplier.py")], cwd=output,
        env={**os.environ, "PYTHONHASHSEED": "0", "PYTHONDONTWRITEBYTECODE": "1"},
        stdout=log, stderr=subprocess.STDOUT, check=False)
(output / "exit.json").write_text(json.dumps({"exit_code": result.returncode}) + "\n")
assert result.returncode == 0
assert all(hashlib.sha256((engine / name).read_bytes()).hexdigest() == checksum for name, checksum in checksums.items())
assert hashlib.sha256((output / relative).read_bytes()).hexdigest() == manifest["benchmark_sha256"]
