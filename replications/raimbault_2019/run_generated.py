"""Replay a bounded interval of the original generated-landscape archive."""

import argparse
import gzip
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
parser.add_argument("--start", type=int, required=True)
parser.add_argument("--stop", type=int, required=True)
args = parser.parse_args()
assert 0 <= args.start < args.stop
engine = args.engine.resolve()
assert (
    subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=engine, text=True).strip()
    == "270cc7f112b3a999b10e02b0f9525038d6d4754d"
)
assert not subprocess.check_output(
    ["git", "status", "--porcelain", "--untracked-files=no"], cwd=engine, text=True
).strip()
reference = args.reference.resolve()
digest = hashlib.sha256()
with gzip.open(reference, "rb") as archive:
    while chunk := archive.read(1024 * 1024):
        digest.update(chunk)
assert (
    digest.hexdigest()
    == "1a2cdf93167571ab2943d488017ace08945e7afd3cd8ac4d1410fb214c79c8f5"
)
args.output.mkdir(parents=True, exist_ok=False)
output = args.output.resolve()
root = Path(__file__).resolve().parent
adapter = root / "GeneratedReplay.java"
model = engine / "sugarscape/HEADLESS_Sugarscape.nlogo"
java = args.jdk.resolve() / "bin/java"
app = args.netlogo.resolve() / "app"
command = [
    str(java),
    "-Djava.awt.headless=true",
    "-Xmx768m",
    "-cp",
    f"{app / 'NetLogo.jar'}:{app}/*",
    str(adapter),
    str(model),
    str(reference),
    str(args.start),
    str(args.stop),
    str(output / "results.csv"),
]
files = [
    model,
    adapter,
    *sorted(model.parent.rglob("*.nls")),
    *sorted((model.parent / "morphology").glob("*.jar")),
]
manifest = {
    "command": command,
    "source_sha256": {
        str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in files
    },
    "java": subprocess.check_output(
        [str(java), "-version"], stderr=subprocess.STDOUT, text=True
    ),
    "dependencies_sha256": {
        str(p): hashlib.sha256(p.read_bytes()).hexdigest()
        for p in sorted(app.glob("*.jar"))
    },
    "reference_sha256": digest.hexdigest(),
    "requested_interval": [args.start, args.stop],
    "steps_each": 10000,
    "scope": "Original generated-landscape interval, including both Gini and all ten native spatial morphology outputs. Full reference, generated ensemble, and fresh phase-diagram contrasts remain separate completion requirements.",
}
(output / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
with (output / "native.log").open("x") as log:
    result = subprocess.run(
        command, cwd=model.parent, stdout=log, stderr=subprocess.STDOUT, check=False
    )
(output / "exit.json").write_text(json.dumps({"exit_code": result.returncode}) + "\n")
assert result.returncode == 0, (
    "Generated-landscape replay failed; preserve partial results and inspect log"
)
