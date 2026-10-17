"""Replay one original selfishness or heterogeneous Blueprints configuration."""

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

ARCHIVE_SHA256 = {
    "selfishness": "e2016f36a9728c23cee025d7a2e63cd2feffe4c36fbd62970e3a7792cb4d19e7",
    "heterogeneous": "c37aa109e59ca8b96cd295b7f022d6bf56f413aabbf246ca432ff5d4360de91a",
}
RELEASE = "b9ca671ab7591c7b3606f2d76c33eda344d626d1"
Model = Literal[
    "none",
    "rawSugarscape",
    "egoisticHalfLookaheadBinary",
    "altruisticHalfLookaheadBinary",
    "benthamHalfLookaheadBinary",
]


class Configuration(BaseModel):
    model_config = ConfigDict(extra="allow")
    seed: int = Field(ge=0)
    agentDecisionModels: list[Model] = Field(min_length=1, max_length=100)
    timesteps: Literal[5000]
    startingAgents: Literal[250]
    startingDiseases: Literal[50]
    headlessMode: Literal[True]
    logfile: str


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("engine", type=Path)
    parser.add_argument("archive", type=Path)
    parser.add_argument("experiment", choices=["selfishness", "heterogeneous"])
    parser.add_argument("entry")
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    engine = args.engine.resolve()
    assert (
        hashlib.sha256(args.archive.read_bytes()).hexdigest()
        == ARCHIVE_SHA256[args.experiment]
    )
    assert (
        subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=engine, text=True
        ).strip()
        == RELEASE
    )
    assert not subprocess.check_output(
        ["git", "status", "--porcelain", "--untracked-files=no"], cwd=engine, text=True
    ).strip()
    with zipfile.ZipFile(args.archive) as archive:
        original = archive.read(args.entry)
    configuration = json.loads(original)
    validated = Configuration.model_validate(configuration)
    assert validated.model_dump() == configuration
    defaults = json.loads((engine / "config.json").read_text())["sugarscapeOptions"]
    if args.experiment == "selfishness":
        assert configuration.keys() == defaults.keys() | {"agentDecisionModel"}
        assert configuration["agentDecisionModels"] == ["none"]
        assert configuration["agentDecisionModel"] == "benthamHalfLookaheadBinary"
        factor = configuration["agentSelfishnessFactor"]
        assert len(factor) == 2 and factor[0] == factor[1] and 0 <= factor[0] <= 1
        assert (
            args.entry
            == f"{factor[0]}-benthamHalfLookaheadBinary{validated.seed}.config"
        )
        effective_models = [configuration["agentDecisionModel"]]
    else:
        assert configuration.keys() == defaults.keys()
        models = configuration["agentDecisionModels"]
        assert len(models) == 100 and set(models) == {
            "benthamHalfLookaheadBinary",
            "egoisticHalfLookaheadBinary",
        }
        count = models.count("benthamHalfLookaheadBinary")
        assert models == ["benthamHalfLookaheadBinary"] * count + [
            "egoisticHalfLookaheadBinary"
        ] * (100 - count)
        assert (
            args.entry
            == f"{count}-benthamHalfLookaheadBinary-egoisticHalfLookaheadBinary{validated.seed}.config"
        )
        effective_models = models
    pins = json.loads(Path(__file__).with_name("source-sha256.json").read_text())[
        "source_sha256"
    ]
    assert {
        p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in engine.glob("*.py")
    } == pins
    args.output.mkdir(parents=True, exist_ok=False)
    output = args.output.resolve()
    (output / "original.config").write_bytes(original)
    configuration["logfile"] = str(output / "trajectory.json")
    config_path = output / "config.json"
    config_path.write_text(json.dumps(configuration, indent=2) + "\n")
    command = [
        sys.executable,
        str(engine / "sugarscape.py"),
        "--conf",
        str(config_path),
    ]
    manifest = {
        "release": RELEASE,
        "archive_sha256": ARCHIVE_SHA256[args.experiment],
        "experiment": args.experiment,
        "effective_models_after_native_normalization": effective_models,
        "entry": args.entry,
        "original_config_sha256": hashlib.sha256(original).hexdigest(),
        "command": command,
        "python": sys.version,
        "pythonhashseed": "0",
        "engine": str(engine),
        "source_sha256": {
            p.name: hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(engine.glob("*.py"))
        },
        "config_sha256": hashlib.sha256(config_path.read_bytes()).hexdigest(),
        "changes": {
            "logfile": {
                "original": validated.logfile,
                "effective": configuration["logfile"],
            }
        },
        "interpretation": "Original archived input and explicitly paper-named v2024.1 release. Native singular decision-model normalization retained; only logfile path changed.",
    }
    (output / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    started = time.monotonic()
    with (
        (output / "stdout.log").open("x") as stdout,
        (output / "stderr.log").open("x") as stderr,
    ):
        subprocess.run(
            command,
            cwd=engine,
            env={**os.environ, "PYTHONHASHSEED": "0", "PYTHONDONTWRITEBYTECODE": "1"},
            stdout=stdout,
            stderr=stderr,
            check=True,
        )
    trajectory = json.loads((output / "trajectory.json").read_text())
    assert [r["timestep"] for r in trajectory] == list(range(len(trajectory)))
    assert trajectory[0]["population"] == 250
    assert all(
        r["seed"] == validated.seed and 0 <= r["population"] <= 2500 for r in trajectory
    )
    array_metrics = {"agentWealths", "agentTimesToLive", "agentTimesToLiveAgeLimited"}
    for row in trajectory:
        assert {
            key for key, value in row.items() if isinstance(value, list)
        } == array_metrics
        assert all(
            math.isfinite(value)
            for key, value in row.items()
            if key not in array_metrics
        )
        assert all(math.isfinite(value) for key in array_metrics for value in row[key])
    final = trajectory[-1]
    assert int(final["timestep"]) == 5000 or int(final["population"]) == 0
    population = int(final["population"])
    result = {
        "entry": args.entry,
        "seed": validated.seed,
        "experiment": args.experiment,
        "effective_models": effective_models,
        "elapsed_seconds": time.monotonic() - started,
        "observations": len(trajectory),
        "final_timestep": int(final["timestep"]),
        "final_population": population,
        "outcome": "dead"
        if population == 0
        else "worse"
        if population < 250
        else "better_or_equal",
        "trajectory_sha256": hashlib.sha256(
            (output / "trajectory.json").read_bytes()
        ).hexdigest(),
    }
    (output / "result.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result))


if __name__ == "__main__":
    main()
