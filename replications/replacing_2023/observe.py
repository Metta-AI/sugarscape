"""Observe the released model; retain native scheduling and random-number use."""
import argparse
import ast
import gzip
import hashlib
import json
import random
import subprocess
import sys
from pathlib import Path

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("engine", type=Path)
parser.add_argument("baseline", type=Path)
parser.add_argument("output", type=Path)
args = parser.parse_args()
engine = args.engine.resolve()
release = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=engine, text=True).strip()
assert release in {"032abd2d2338aadc5ad0287dae7520539f7af57b", "d57d39dd034fe5926ad51ed5f3f7b6837a2210ac"}
assert json.loads((args.baseline / "manifest.json").read_text())["release"] == release
assert not subprocess.check_output(["git", "status", "--porcelain", "--untracked-files=no"], cwd=engine, text=True).strip()
source = engine / "sugarscape.py"
sys.path.insert(0, str(engine))
import sugarscape

# Read the actual CLI defaults, including keys absent from example files.
main = [node for node in ast.parse(source.read_text()).body if isinstance(node, ast.If)][-1]
assignment = main.body[0]
assert isinstance(assignment, ast.Assign) and assignment.targets[0].id == "configuration"
defaults = ast.literal_eval(assignment.value)
configuration = sugarscape.parseConfiguration(str(args.baseline / "config.json"), defaults)
configuration = sugarscape.verifyConfiguration(configuration)
assert configuration["headlessMode"] and not configuration["screenshots"]
args.output.mkdir(parents=True, exist_ok=False)
output = args.output.resolve()
configuration["logfile"] = str(output / "trajectory.json")
(output / "effective-config.json").write_text(json.dumps(configuration, indent=2) + "\n")
(output / "manifest.json").write_text(json.dumps({
    "baseline": str(args.baseline.resolve()), "source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
    "observer_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(), "python": sys.version,
    "agent_columns": ["id", "x", "y", "vision", "sugar_metabolism", "age", "disease_count", "season", "hemisphere"],
    "timing": "Initialization and after each native doTimestep; no sorting or random draws. Native endSimulation exits after closing its log."
}, indent=2) + "\n")

class ObservedSugarscape(sugarscape.Sugarscape):
    def snapshot(self):
        record = {"timestep": self.timestep, "population": len(self.agents),
                  "agents": [[a.ID, a.cell.x, a.cell.y, a.vision, a.sugarMetabolism, a.age,
                              len(a.diseases), a.cell.season, a.cell.hemisphere] for a in self.agents]}
        observations.write(json.dumps(record, separators=(",", ":")) + "\n")

    def doTimestep(self):
        super().doTimestep()
        self.snapshot()

random.seed(configuration["seed"])
with gzip.open(output / "observations.jsonl.gz", "xt") as observations:
    simulation = ObservedSugarscape(configuration)
    simulation.snapshot()
    simulation.runSimulation(configuration["timesteps"])
