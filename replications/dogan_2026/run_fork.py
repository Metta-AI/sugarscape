"""Run a complete original experiment from the Metta-AI study's pinned source bundle."""
import argparse
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import platform
import subprocess
import sys

experiments = {
    "canonical": "run_canonical_sweep.py", "horizon": "run_stage5_horizon.py",
    "composition": "run_composition_sweep.py", "levy": "run_stage5_D_sweep.py",
    "perseed": "run_stage5_perseed_thresholds.py", "multiplier": "run_stage5_uhi_multiplier.py",
    "reports": "analyze_canonical.py",
}
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("experiment", choices=experiments)
parser.add_argument("output", type=Path)
parser.add_argument("--canonical", type=Path, help="Completed native canonical run, required for multiplier and reports")
args = parser.parse_args()
if (args.experiment in {"multiplier", "reports"}) != (args.canonical is not None):
    parser.error("--canonical is required only for multiplier and reports")
root = Path(__file__).resolve().parent
vendor = root / "vendor"
provenance_bytes = (root / "vendor-provenance.json").read_bytes()
provenance = json.loads(provenance_bytes)
assert platform.python_version() == "3.12.4"
for line in (root / "environment.txt").read_text().splitlines():
    name, version = line.split("==")
    assert importlib.metadata.version(name) == version
for name, checksum in provenance["files_sha256"].items():
    assert hashlib.sha256((vendor / name).read_bytes()).hexdigest() == checksum
inputs = {}
if args.experiment in {"multiplier", "reports"}:
    assert json.loads((args.canonical / "exit.json").read_text())["exit_code"] == 0
    names = ["part_b_stage5_main.csv"] if args.experiment == "multiplier" else [
        "part_a_stage4_static.csv", "part_b_stage5_main.csv", "part_b_agent_step300.csv", "part_c_welfare_sensitivity.csv"]
    inputs = {name: (args.canonical / "results/canonical" / name).read_bytes() for name in names}
args.output.mkdir(parents=True, exist_ok=False)
output = args.output.resolve()
if inputs:
    (output / "results/canonical").mkdir(parents=True)
    for name, raw in inputs.items():
        (output / "results/canonical" / name).write_bytes(raw)
command = [sys.executable, "-u", str(vendor / experiments[args.experiment])]
manifest = {"experiment": args.experiment, "command": command, "python": sys.version,
    "platform": platform.platform(), "provenance_sha256": hashlib.sha256(provenance_bytes).hexdigest(),
    "source_sha256": provenance["files_sha256"], "author_revision": provenance["revision"],
    "environment_sha256": hashlib.sha256((root / "environment.txt").read_bytes()).hexdigest(),
    "input_sha256": {name: hashlib.sha256(raw).hexdigest() for name, raw in inputs.items()},
    "scope": "Original author implementation integrated into the Metta-AI fork; not an independent implementation or a model-equivalence claim for the DTL engine."}
(output / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
with (output / "native.log").open("x") as log:
    result = subprocess.run(command, cwd=output, stdout=log, stderr=subprocess.STDOUT,
        env={**os.environ, "PYTHONHASHSEED": "0", "PYTHONDONTWRITEBYTECODE": "1"}, check=False)
(output / "exit.json").write_text(json.dumps({"exit_code": result.returncode}) + "\n")
assert result.returncode == 0, "Native experiment failed; see retained log"
for name, checksum in provenance["files_sha256"].items():
    assert hashlib.sha256((vendor / name).read_bytes()).hexdigest() == checksum
for name, raw in inputs.items():
    assert (output / "results/canonical" / name).read_bytes() == raw
results = {str(p.relative_to(output)): hashlib.sha256(p.read_bytes()).hexdigest()
           for p in sorted((output / "results").rglob('*')) if p.is_file()}
assert results
(output / "output-sha256.json").write_text(json.dumps(results, indent=2) + "\n")
print(json.dumps({"experiment": args.experiment, "exit_code": 0, "output_files": len(results)}))
