"""Regenerate the manuscript's two figures from complete fresh canonical data."""
import argparse
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

import numpy as np
from PIL import Image

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("engine", type=Path)
parser.add_argument("canonical", type=Path)
parser.add_argument("output", type=Path)
args = parser.parse_args()
engine = args.engine.resolve()
revision = "0b6a3df470388f60535d8ffb67c34a7f9fa0059a"
assert subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=engine, text=True).strip() == revision
script = engine / "make_paper_figures.py"
assert hashlib.sha256(script.read_bytes()).hexdigest() == "4d22c1a011db0cd0212d6627c5539c62b0633c0aae4220d491503e532443e826"
assert json.loads((args.canonical / "exit.json").read_text())["exit_code"] == 0
canonical_manifest = json.loads((args.canonical / "manifest.json").read_text())
relative = "results/canonical/part_b_stage5_main.csv"
data = (args.canonical / relative).read_bytes()
assert hashlib.sha256(data).hexdigest() == canonical_manifest["reference_sha256"][relative]
output = args.output.resolve()
output.mkdir(parents=True, exist_ok=False)
(output / "results/canonical").mkdir(parents=True)
(output / relative).write_bytes(data)
shutil.copyfile(script, output / script.name)
manifest = {"revision": revision, "input_sha256": hashlib.sha256(data).hexdigest(),
            "script_sha256": hashlib.sha256(script.read_bytes()).hexdigest(), "python": sys.version,
            "packages": {name: importlib.metadata.version(name) for name in ["numpy", "pandas", "matplotlib", "pillow"]}}
(output / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
with (output / "native.log").open("x") as log:
    result = subprocess.run([sys.executable, str(output / script.name)], cwd=output,
                            env={**os.environ, "MPLBACKEND": "Agg"}, stdout=log, stderr=subprocess.STDOUT, check=False)
(output / "exit.json").write_text(json.dumps({"exit_code": result.returncode}) + "\n")
assert result.returncode == 0
comparisons = []
for name in ["fig_gini_inversion.png", "fig_welfare_robustness.png"]:
    relative = "results/canonical/" + name
    original = subprocess.check_output(["git", "show", f"{revision}:{relative}"], cwd=engine)
    assert (engine / relative).read_bytes() == original
    generated = (output / relative).read_bytes()
    with Image.open(engine / relative) as image:
        left = np.asarray(image.convert("RGBA"))
    with Image.open(output / relative) as image:
        right = np.asarray(image.convert("RGBA"))
    same_shape = left.shape == right.shape
    comparisons.append({"file": name, "original_sha256": hashlib.sha256(original).hexdigest(),
                        "generated_sha256": hashlib.sha256(generated).hexdigest(),
                        "byte_identical": original == generated, "original_shape": list(left.shape),
                        "generated_shape": list(right.shape),
                        "pixels_identical": bool(same_shape and np.array_equal(left, right))})
report = {"comparisons": comparisons,
          "scope": "Fresh-data replay of manuscript-referenced native figures. Table means have separate independent audits; image equality alone does not validate policy claims."}
(output / "comparison.json").write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps(report))
