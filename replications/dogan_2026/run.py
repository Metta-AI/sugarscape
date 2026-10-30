"""Run the pinned author's complete canonical sweep in an isolated output directory."""
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
revision = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=engine, text=True).strip()
assert revision == "0b6a3df470388f60535d8ffb67c34a7f9fa0059a"
assert not subprocess.check_output(["git", "status", "--porcelain", "--untracked-files=no"], cwd=engine, text=True).strip()
assert platform.python_version() == "3.12.4"
versions = {name: importlib.metadata.version(name) for name in ["mesa", "numpy", "pandas", "matplotlib"]}
assert versions == {"mesa": "3.5.1", "numpy": "2.4.2", "pandas": "2.3.3", "matplotlib": "3.10.8"}
args.output.mkdir(parents=True, exist_ok=False)
output = args.output.resolve()
files = [*sorted((engine / "sugarscape_ai_tax").glob("*.py")), engine / "sugarscape_ai_tax/sugar-map.txt",
         engine / "run_canonical_sweep.py", engine / "requirements.txt", engine / "sugarscape_ai_tax.pdf"]
references = sorted((engine / "results/canonical").glob("*.csv"))
manifest = {"repository": "https://github.com/dgnerg867-ux/sugarscape", "revision": revision,
            "installed_distributions": {d.metadata["Name"]: d.version for d in importlib.metadata.distributions()},
            "python": sys.version, "platform": platform.platform(), "versions": versions,
            "pythonhashseed": "0", "source_sha256": {str(p.relative_to(engine)): hashlib.sha256(p.read_bytes()).hexdigest() for p in files},
            "reference_sha256": {str(p.relative_to(engine)): hashlib.sha256(p.read_bytes()).hexdigest() for p in references},
            "scope": "Complete original canonical sweep: 25 static, 105 transition, 75 welfare-sensitivity runs, plus two original threshold-calibration runs. Additional paper robustness experiments remain outside this batch."}
(output / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
with (output / "native.log").open("x") as log:
    result = subprocess.run([sys.executable, "-u", str(engine / "run_canonical_sweep.py")], cwd=output,
                            env={**os.environ, "PYTHONHASHSEED": "0", "PYTHONDONTWRITEBYTECODE": "1"},
                            stdout=log, stderr=subprocess.STDOUT, check=False)
(output / "exit.json").write_text(json.dumps({"exit_code": result.returncode}) + "\n")
assert result.returncode == 0, "Original sweep failed; inspect retained log"
