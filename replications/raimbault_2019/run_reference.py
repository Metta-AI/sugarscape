"""Run the full archived fixed-landscape reference without changing the model."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("engine", type=Path)
parser.add_argument("netlogo", type=Path)
parser.add_argument("jdk", type=Path)
parser.add_argument("reference", type=Path)
parser.add_argument("output", type=Path)
parser.add_argument("--start", type=int, default=0)
parser.add_argument("--stop", type=int, default=55000)
args = parser.parse_args()
assert 0 <= args.start < args.stop <= 55000
engine = args.engine.resolve()
assert subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=engine, text=True).strip() == "270cc7f112b3a999b10e02b0f9525038d6d4754d"
assert not subprocess.check_output(["git", "status", "--porcelain", "--untracked-files=no"], cwd=engine, text=True).strip()
reference = args.reference.resolve()
assert hashlib.sha256(reference.read_bytes()).hexdigest() == "2fc276934c6c50994a2c24196b7da4231383ef3d13f86804b5c38cb0d1d93add"
assert len(reference.read_text().splitlines()) == 55001
args.output.mkdir(parents=True, exist_ok=False)
output = args.output.resolve()
root = Path(__file__).resolve().parent
adapter = root / "BatchReplay.java"
model = engine / "sugarscape/HEADLESS_Sugarscape.nlogo"
java = args.jdk.resolve() / "bin/java"
app = args.netlogo.resolve() / "app"
command = [str(java), "-Djava.awt.headless=true", "-Xmx768m", "-cp", f"{app / 'NetLogo.jar'}:{app}/*",
           str(adapter), str(model), str(reference), str(args.start), str(args.stop), str(output / "results.csv")]
files = [model, adapter, *sorted(model.parent.glob("*.nls")), model.parent / "setup/sugar-map.txt"]
manifest = {"command": command, "source_sha256": {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in files},
            "java": subprocess.check_output([str(java), "-version"], stderr=subprocess.STDOUT, text=True),
            "dependencies_sha256": {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(app.glob("*.jar"))},
            "reference_sha256": hashlib.sha256(reference.read_bytes()).hexdigest(), "rows": 55000, "steps_each": 10000,
            "scope": "Complete original fixed-landscape reference; generated landscapes and fresh phase-diagram contrasts remain separate required experiments."}
(output / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
with (output / "native.log").open("x") as log:
    result = subprocess.run(command, cwd=model.parent, stdout=log, stderr=subprocess.STDOUT, check=False)
(output / "exit.json").write_text(json.dumps({"exit_code": result.returncode}) + "\n")
assert result.returncode == 0, "Reference replay failed; preserve partial results and inspect log"
