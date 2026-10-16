"""Execute declared original robustness scripts without overwriting author results."""
import argparse
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import platform
import subprocess
import sys

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("engine", type=Path)
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
experiments = [
    {"script": "run_stage5_horizon.py", "output": "results/canonical/horizon_sweep.csv", "rows": 45, "horizon": 600},
    {"script": "run_composition_sweep.py", "output": "results/canonical/composition_sweep.csv", "rows": 210, "horizon": 300},
    {"script": "run_stage5_D_sweep.py", "output": "results/stage5_D_sweep.csv", "rows": 75, "horizon": 300},
    {"script": "run_stage5_perseed_thresholds.py", "output": "results/stage5_perseed_thresholds.csv", "rows": 105, "horizon": 300},
]
files = [*sorted((engine / "sugarscape_ai_tax").glob("*.py")), engine / "sugarscape_ai_tax/sugar-map.txt",
         *[engine / e["script"] for e in experiments]]
checksums = {str(p.relative_to(engine)): hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
args.output.mkdir(parents=True, exist_ok=False)
output = args.output.resolve()
manifest = {"engine": str(engine), "python": sys.version, "experiments": experiments, "source_sha256": checksums,
            "environment_lock_sha256": hashlib.sha256((root / "environment.txt").read_bytes()).hexdigest(),
            "limitation": "Original levy and per-seed threshold CSVs are not in the public deposit. Those outputs require comparison with manuscript claims, not fabricated reference data. UHI multiplier study awaits fresh canonical benchmarks."}
(output / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
with (output / "completed.jsonl").open("x") as completed:
    for experiment in experiments:
        assert all(hashlib.sha256((engine / name).read_bytes()).hexdigest() == checksum for name, checksum in checksums.items())
        with (output / (experiment["script"] + ".log")).open("x") as log:
            result = subprocess.run([sys.executable, "-u", str(engine / experiment["script"])], cwd=output,
                                    env={**os.environ, "PYTHONHASHSEED": "0", "PYTHONDONTWRITEBYTECODE": "1"},
                                    stdout=log, stderr=subprocess.STDOUT, check=False)
        completed.write(json.dumps({"script": experiment["script"], "exit_code": result.returncode}) + "\n")
        completed.flush()
        assert result.returncode == 0, "Original experiment failed; inspect retained log"
