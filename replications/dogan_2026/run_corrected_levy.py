"""Run the original 75-case levy sweep with only the declared conservation patch."""
import argparse
import gzip
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
root = Path(__file__).resolve().parent
revision = "0b6a3df470388f60535d8ffb67c34a7f9fa0059a"
assert platform.python_version() == "3.12.4"
for line in (root / "environment.txt").read_text().splitlines():
    name, version = line.split("==")
    assert importlib.metadata.version(name) == version
output = args.output.resolve()
output.mkdir(parents=True, exist_ok=False)
variant = output / "source"
variant.mkdir()
files = ["sugarscape_ai_tax/model.py", "sugarscape_ai_tax/agents.py", "sugarscape_ai_tax/__init__.py",
         "sugarscape_ai_tax/sugar-map.txt", "run_stage5_D_sweep.py", "LICENSE", "NOTICE", "LICENSES/Apache-2.0.txt"]
original = {}
for name in files:
    data = subprocess.check_output(["git", "show", f"{revision}:{name}"], cwd=args.engine)
    target = variant / name
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(data)
    original[name] = hashlib.sha256(data).hexdigest()
patch = gzip.decompress((root / "conserving-levy.patch.gz").read_bytes())
(output / "conserving-levy.patch").write_bytes(patch)
subprocess.run(["patch", "--batch", "-p1", "-i", str(output / "conserving-levy.patch")], cwd=variant, check=True)
modified = {name: hashlib.sha256((variant / name).read_bytes()).hexdigest() for name in files}
assert [name for name in files if original[name] != modified[name]] == ["sugarscape_ai_tax/model.py"]
manifest = {"revision": revision, "python": sys.version, "original_sha256": original, "source_sha256": modified,
            "patch_sha256": hashlib.sha256(patch).hexdigest(),
            "protocol_sha256": hashlib.sha256((root / "LEVY_DIAGNOSTIC.md").read_bytes()).hexdigest(),
            "environment_sha256": hashlib.sha256((root / "environment.txt").read_bytes()).hexdigest(),
            "scope": "Declared accounting correction variant, not the unmodified author replication.",
            "runs": 75, "steps": 300}
(output / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
with (output / "native.log").open("x") as log:
    result = subprocess.run([sys.executable, "-u", str(variant / "run_stage5_D_sweep.py")], cwd=output,
                            env={**os.environ, "PYTHONHASHSEED": "0", "PYTHONDONTWRITEBYTECODE": "1"},
                            stdout=log, stderr=subprocess.STDOUT, check=False)
(output / "exit.json").write_text(json.dumps({"exit_code": result.returncode}) + "\n")
assert result.returncode == 0, "Corrected native sweep failed; inspect retained log"
assert all(hashlib.sha256((variant / name).read_bytes()).hexdigest() == checksum for name, checksum in modified.items())
csv = output / "results/stage5_D_sweep.csv"
(output / "output-sha256.json").write_text(json.dumps({"results/stage5_D_sweep.csv": hashlib.sha256(csv.read_bytes()).hexdigest()}) + "\n")
