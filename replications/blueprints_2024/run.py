"""Run a complete Blueprints homogeneous-society experiment on the historical release."""

import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import subprocess
import sys
import time
from typing import Literal

from pydantic import BaseModel, Field


class Experiment(BaseModel):
    seed: int = Field(ge=0)
    model: Literal["rawSugarscape", "egoist", "altruist", "bentham"]
    timesteps: Literal[5000] = 5000
    release: Literal["651925a5f7634fa3dd0f66c0621e7118e89807f8"] = "651925a5f7634fa3dd0f66c0621e7118e89807f8"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("engine", type=Path)
    parser.add_argument("--seed", type=int, required=True)
    parser.add_argument("--model", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    experiment = Experiment(seed=args.seed, model=args.model)
    engine = args.engine.resolve()
    revision = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=engine, text=True).strip()
    assert revision == experiment.release
    assert not subprocess.check_output(["git", "status", "--porcelain", "--untracked-files=no"], cwd=engine, text=True).strip()
    configuration = json.loads((engine / "config.json").read_text())["sugarscapeOptions"]
    assert configuration["startingAgents"] == 250
    assert configuration["startingDiseases"] == 50
    assert configuration["environmentMaxTribes"] == 3
    assert configuration["environmentSeasonInterval"] == 0
    assert configuration["environmentPollutionTimeframe"] == [0, 0]
    args.output.mkdir(parents=True, exist_ok=False)
    output = args.output.resolve()
    configuration.update(seed=experiment.seed, agentDecisionModels=[experiment.model], timesteps=5000,
                         headlessMode=True, debugMode=["none"], logfile=str(output / "trajectory.json"))
    config_path = output / "config.json"
    config_path.write_text(json.dumps(configuration, indent=2) + "\n")
    command = [sys.executable, str(engine / "sugarscape.py"), "--conf", str(config_path)]
    manifest = {
        "experiment": experiment.model_dump(), "status": "started", "command": command,
        "python": sys.version, "pythonhashseed": "0", "engine": str(engine),
        "source_sha256": {path.name: hashlib.sha256(path.read_bytes()).hexdigest()
                          for path in sorted(engine.glob("*.py"))},
        "config_sha256": hashlib.sha256(config_path.read_bytes()).hexdigest(),
        "interpretation": "Historical-release candidate; the paper's exact code revision and original seeds are unreported.",
    }
    (output / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    started = time.monotonic()
    with (output / "stdout.log").open("x") as stdout, (output / "stderr.log").open("x") as stderr:
        subprocess.run(command, cwd=engine, env={**os.environ, "PYTHONHASHSEED": "0", "PYTHONDONTWRITEBYTECODE": "1"},
                       stdout=stdout, stderr=stderr, check=True)
    trajectory = json.loads((output / "trajectory.json").read_text())
    assert [row["timestep"] for row in trajectory] == list(range(len(trajectory)))
    assert trajectory[0]["population"] == 250
    assert all(row["seed"] == experiment.seed and row["population"] >= 0 for row in trajectory)
    assert all(math.isfinite(value) for row in trajectory for value in row.values())
    final = trajectory[-1]
    assert int(final["timestep"]) == 5000 or int(final["population"]) == 0
    population = int(final["population"])
    outcome = "dead" if population == 0 else "better" if population > 250 else "worse_or_equal"
    result = {"experiment": experiment.model_dump(), "elapsed_seconds": time.monotonic() - started,
              "observations": len(trajectory), "final_timestep": int(final["timestep"]),
              "final_population": population, "outcome": outcome,
              "trajectory_sha256": hashlib.sha256((output / "trajectory.json").read_bytes()).hexdigest()}
    (output / "result.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result))


if __name__ == "__main__":
    main()
