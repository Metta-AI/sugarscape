"""Retain the native extended log while reconstructing the original reporting schedule."""
from pathlib import Path
import ast
import argparse
import copy
import hashlib
import importlib
import json
import random
import sys

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("output", type=Path)
parser.add_argument("configuration", type=Path)
args = parser.parse_args()
root = args.output.resolve()
base = Path("/Users/relh/Code/workspace")
engine = base / "sugarscape-dtl-replacing-reference"
previous = base / "sugarscape-replication-evidence/replacing-trade-long-horizon-001"
manifest = json.loads((previous / "manifest.json").read_bytes())
assert sys.version == manifest["python"]
assert all(hashlib.sha256((engine / name).read_bytes()).hexdigest() == digest for name, digest in manifest["source_sha256"].items())
source = engine / "sugarscape.py"
sys.path.insert(0, str(engine))
sugarscape = importlib.import_module("sugarscape")

main = [n for n in ast.parse(source.read_text()).body if isinstance(n, ast.If)][-1]
assignment = main.body[0]
assert isinstance(assignment, ast.Assign) and assignment.targets[0].id == "configuration"
defaults = ast.literal_eval(assignment.value)
configuration = sugarscape.verifyConfiguration(sugarscape.parseConfiguration(str(args.configuration), defaults))
assert configuration["headlessMode"] and not configuration["screenshots"] and configuration["timesteps"] == 10000
configuration["logfile"] = str(root / "trajectory.json")
(root / "effective-config.json").write_text(json.dumps(configuration, indent=2) + "\n")
(root / "manifest.json").write_text(json.dumps({"source_sha256": manifest["source_sha256"], "observer_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(), "python": sys.version, "baseline": str(previous), "scope": "Qualified passive reporting; every original500step record must reconstruct exactly. No simulation rule changes."}, indent=2) + "\n")

class ObservedSugarscape(sugarscape.Sugarscape):
    def updateRuntimeStats(self):
        super().updateRuntimeStats()
        if self.timestep <= 500:
            rng_before = random.getstate()
            record = copy.deepcopy(self.runtimeStats)
            if self.timestep in (125, 250, 375, 500):
                record["agentWealths"] = [a.wealth for a in self.agents]
                record["agentTimesToLive"] = [a.findTimeToLive() for a in self.agents]
                record["agentTimesToLiveAgeLimited"] = [a.findTimeToLive(True) for a in self.agents]
            if self.timestep == 500:
                for agent in self.agents:
                    record["totalMetabolismCost"] += agent.sugarMetabolism + agent.spiceMetabolism
                record["environmentWealthCreated"] = 0
                record["environmentWealthTotal"] = 0
                for i in range(self.environment.height):
                    for j in range(self.environment.width):
                        cell = self.environment.grid[i][j]
                        record["environmentWealthCreated"] += cell.sugarLastProduced + cell.spiceLastProduced
                        record["environmentWealthTotal"] += cell.sugar + cell.spice
            assert random.getstate() == rng_before
            observations.write(json.dumps(record) + "\n")
            observations.flush()

random.seed(configuration["seed"])
with (root / "original-schedule.jsonl").open("x") as observations:
    simulation = ObservedSugarscape(configuration)
    simulation.runSimulation(configuration["timesteps"])
