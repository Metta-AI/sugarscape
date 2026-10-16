"""Replay one archived Blueprints configuration with the schema-matching release."""
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
import zipfile

from pydantic import BaseModel, ConfigDict, Field

ARCHIVE_SHA256 = "319c38c77cdeb9f3bd618ce6c57e14e93c35e2be282c01332d42cff58327f525"
RELEASE = "b9ca671ab7591c7b3606f2d76c33eda344d626d1"
Model = Literal["rawSugarscape", "egoisticHalfLookaheadBinary", "altruisticHalfLookaheadBinary", "benthamHalfLookaheadBinary"]

class Configuration(BaseModel):
    model_config = ConfigDict(extra="allow")
    seed: int = Field(ge=0)
    agentDecisionModels: list[Model] = Field(min_length=1, max_length=1)
    timesteps: Literal[5000]
    startingAgents: Literal[250]
    startingDiseases: Literal[50]
    headlessMode: Literal[True]
    logfile: str


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("engine", type=Path)
    parser.add_argument("archive", type=Path)
    parser.add_argument("entry")
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    engine = args.engine.resolve()
    assert hashlib.sha256(args.archive.read_bytes()).hexdigest() == ARCHIVE_SHA256
    assert subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=engine, text=True).strip() == RELEASE
    assert not subprocess.check_output(["git", "status", "--porcelain", "--untracked-files=no"], cwd=engine, text=True).strip()
    with zipfile.ZipFile(args.archive) as archive:
        original = archive.read(args.entry)
    configuration = json.loads(original)
    validated = Configuration.model_validate(configuration)
    assert validated.model_dump() == configuration
    defaults = json.loads((engine / "config.json").read_text())["sugarscapeOptions"]
    assert configuration.keys() == defaults.keys(), "No archived option may be silently ignored or supplemented"
    assert args.entry == f"{validated.agentDecisionModels[0]}{validated.seed}.config"
    args.output.mkdir(parents=True, exist_ok=False)
    output = args.output.resolve()
    (output / "original.config").write_bytes(original)
    configuration["logfile"] = str(output / "trajectory.json")
    config_path = output / "config.json"
    config_path.write_text(json.dumps(configuration, indent=2) + "\n")
    command = [sys.executable, str(engine / "sugarscape.py"), "--conf", str(config_path)]
    manifest = {
        "release": RELEASE, "archive_sha256": ARCHIVE_SHA256, "entry": args.entry,
        "original_config_sha256": hashlib.sha256(original).hexdigest(),
        "command": command, "python": sys.version, "pythonhashseed": "0", "engine": str(engine),
        "source_sha256": {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(engine.glob("*.py"))},
        "config_sha256": hashlib.sha256(config_path.read_bytes()).hexdigest(),
        "changes": {"logfile": {"original": validated.logfile, "effective": configuration["logfile"]}},
        "interpretation": "Original archived input; release predates archive and matches every configuration key. Exact author code revision still unverified.",
    }
    (output / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    started = time.monotonic()
    with (output / "stdout.log").open("x") as stdout, (output / "stderr.log").open("x") as stderr:
        subprocess.run(command, cwd=engine, env={**os.environ, "PYTHONHASHSEED": "0", "PYTHONDONTWRITEBYTECODE": "1"}, stdout=stdout, stderr=stderr, check=True)
    trajectory = json.loads((output / "trajectory.json").read_text())
    assert [r["timestep"] for r in trajectory] == list(range(len(trajectory)))
    assert trajectory[0]["population"] == 250
    assert all(r["seed"] == validated.seed and 0 <= r["population"] <= 2500 for r in trajectory)
    array_metrics = {"agentWealths", "agentTimesToLive", "agentTimesToLiveAgeLimited"}
    for row in trajectory:
        assert {key for key, value in row.items() if isinstance(value, list)} == array_metrics
        assert all(math.isfinite(value) for key, value in row.items() if key not in array_metrics)
        assert all(math.isfinite(value) for key in array_metrics for value in row[key])
    final = trajectory[-1]
    assert int(final["timestep"]) == 5000 or int(final["population"]) == 0
    population = int(final["population"])
    result = {"entry": args.entry, "seed": validated.seed, "model": validated.agentDecisionModels[0],
              "elapsed_seconds": time.monotonic() - started, "observations": len(trajectory),
              "final_timestep": int(final["timestep"]), "final_population": population,
              "outcome": "dead" if population == 0 else "worse" if population < 250 else "better_or_equal",
              "trajectory_sha256": hashlib.sha256((output / "trajectory.json").read_bytes()).hexdigest()}
    (output / "result.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result))

if __name__ == "__main__":
    main()
