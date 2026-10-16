"""Run the released showcase configurations without modifying simulation rules."""
import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import subprocess
import sys
from typing import Literal

from pydantic import BaseModel, Field

RELEASES = {
    "032abd2d2338aadc5ad0287dae7520539f7af57b": "First stable archive, December 20, 2023",
    "d57d39dd034fe5926ad51ed5f3f7b6837a2210ac": "Last upstream revision before December 14–15, 2023 conference; not a verified paper pin",
}

class Experiment(BaseModel):
    scenario: Literal["seasonal_migration", "reproduction_limited", "disease_basic"]
    seed: int = Field(ge=0)

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("engine", type=Path)
parser.add_argument("scenario")
parser.add_argument("seed", type=int)
parser.add_argument("output", type=Path)
args = parser.parse_args()
experiment = Experiment(scenario=args.scenario, seed=args.seed)
engine = args.engine.resolve()
release = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=engine, text=True).strip()
assert release in RELEASES
assert not subprocess.check_output(["git", "status", "--porcelain", "--untracked-files=no"], cwd=engine, text=True).strip()
source = engine / "examples" / f"{experiment.scenario}.json"
original = json.loads(source.read_text())
assert original["seed"] == 12345 and original["timesteps"] == 500
configuration = dict(original)
# Figure 2 extends to 2500; retain published example horizons for the other pilots.
horizon = 2500 if experiment.scenario == "reproduction_limited" else 500
args.output.mkdir(parents=True, exist_ok=False)
output = args.output.resolve()
configuration.update(seed=experiment.seed, timesteps=horizon, headlessMode=True, debugMode=["none"], logfile=str(output / "trajectory.json"))
config = output / "config.json"
config.write_text(json.dumps(configuration, indent=2) + "\n")
command = [sys.executable, str(engine / "sugarscape.py"), "--conf", str(config)]
manifest = {"experiment": experiment.model_dump(), "release": release, "release_selection": RELEASES[release], "python": sys.version,
            "command": command, "pythonhashseed": "0", "source_config_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
            "source_sha256": {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(engine.glob("*.py"))},
            "config_sha256": hashlib.sha256(config.read_bytes()).hexdigest(),
            "overrides": {k: configuration[k] for k in ["seed", "timesteps", "headlessMode", "debugMode", "logfile"]},
            "limitation": "Neither revision is explicitly pinned as the paper's exact code. Seasonal/disease pilots use the released 500-step horizon, not a verified figure sampling schedule."}
(output / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
with (output / "stdout.log").open("x") as stdout, (output / "stderr.log").open("x") as stderr:
    subprocess.run(command, cwd=engine, env={**os.environ, "PYTHONHASHSEED": "0", "PYTHONDONTWRITEBYTECODE": "1"}, stdout=stdout, stderr=stderr, check=True)
trajectory = json.loads((output / "trajectory.json").read_text())
assert [r["timestep"] for r in trajectory] == list(range(len(trajectory)))
assert trajectory[0]["population"] == original["startingAgents"]
arrays = {"agentWealths", "agentTimesToLive", "agentTimesToLiveAgeLimited"}
for row in trajectory:
    assert row["seed"] == experiment.seed and 0 <= row["population"] <= 2500
    assert {k for k, v in row.items() if isinstance(v, list)} == arrays
    assert all(math.isfinite(v) for k, v in row.items() if k not in arrays)
    assert all(math.isfinite(v) for k in arrays for v in row[k])
assert trajectory[-1]["timestep"] == horizon or trajectory[-1]["population"] == 0
result = {"observations": len(trajectory), "final_timestep": trajectory[-1]["timestep"], "final_population": trajectory[-1]["population"],
          "minimum_population": min(r["population"] for r in trajectory), "maximum_population": max(r["population"] for r in trajectory),
          "trajectory_sha256": hashlib.sha256((output / "trajectory.json").read_bytes()).hexdigest(),
          "interpretation": "Operational replay; qualitative paper targets and historical-code equivalence remain unvalidated."}
(output / "result.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps(result))
