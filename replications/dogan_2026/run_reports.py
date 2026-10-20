"""Regenerate the author's canonical reports from the completed fresh sweep."""
import argparse
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import subprocess
import sys

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("engine", type=Path)
parser.add_argument("canonical", type=Path)
parser.add_argument("output", type=Path)
args = parser.parse_args()
engine = args.engine.resolve()
assert subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=engine, text=True).strip() == "0b6a3df470388f60535d8ffb67c34a7f9fa0059a"
assert not subprocess.check_output(["git", "status", "--porcelain", "--untracked-files=no"], cwd=engine, text=True).strip()
assert json.loads((args.canonical / "exit.json").read_text())["exit_code"] == 0
for line in Path(__file__).with_name("environment.txt").read_text().splitlines():
    name, version = line.split("==")
    assert importlib.metadata.version(name) == version
canonical_manifest = json.loads((args.canonical / "manifest.json").read_text())
for name, checksum in canonical_manifest["source_sha256"].items():
    assert hashlib.sha256((engine / name).read_bytes()).hexdigest() == checksum
args.output.mkdir(parents=True, exist_ok=False)
output = args.output.resolve()
data = output / "results/canonical"
data.mkdir(parents=True)
inputs = {}
for name in ["part_a_stage4_static.csv", "part_b_stage5_main.csv", "part_b_agent_step300.csv", "part_c_welfare_sensitivity.csv"]:
    raw = (args.canonical / "results/canonical" / name).read_bytes()
    inputs[name] = hashlib.sha256(raw).hexdigest()
    (data / name).write_bytes(raw)
script = engine / "analyze_canonical.py"
manifest = {"engine": str(engine), "python": sys.version, "canonical": str(args.canonical.resolve()),
    "canonical_manifest_sha256": hashlib.sha256((args.canonical / "manifest.json").read_bytes()).hexdigest(),
    "analysis_script_sha256": hashlib.sha256(script.read_bytes()).hexdigest(), "input_sha256": inputs,
    "scope": "Unmodified author report generation from fresh native outputs, separate from independent manuscript audits."}
(output / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
with (output / "native.log").open("x") as log:
    result = subprocess.run([sys.executable, "-u", str(script)], cwd=output,
        env={**os.environ, "PYTHONHASHSEED": "0", "PYTHONDONTWRITEBYTECODE": "1"},
        stdout=log, stderr=subprocess.STDOUT, check=False)
(output / "exit.json").write_text(json.dumps({"exit_code": result.returncode}) + "\n")
assert result.returncode == 0
assert hashlib.sha256(script.read_bytes()).hexdigest() == manifest["analysis_script_sha256"]
assert all(hashlib.sha256((data / name).read_bytes()).hexdigest() == checksum for name, checksum in inputs.items())
reports = sorted(data.glob("*.txt"))
assert len(reports) == 9
comparison = []
for report in reports:
    reference = engine / "results/canonical" / report.name
    comparison.append({"file": report.name, "fresh_sha256": hashlib.sha256(report.read_bytes()).hexdigest(),
        "reference_sha256": hashlib.sha256(reference.read_bytes()).hexdigest(),
        "byte_identical": report.read_bytes() == reference.read_bytes()})
(output / "comparison.json").write_text(json.dumps(comparison, indent=2) + "\n")
print(json.dumps(comparison))
assert all(row["byte_identical"] for row in comparison), "Report differs from deposit; inspect evidence"
