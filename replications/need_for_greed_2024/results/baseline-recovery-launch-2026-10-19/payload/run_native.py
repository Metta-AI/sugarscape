"""Run one exact deposited Need for Greed input with a required wall-time bound."""

import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time
from typing import Literal
import zipfile

from pydantic import BaseModel, ConfigDict, Field

ARCHIVE_SHA256 = "e41c89ed31811b2d100c0a54f9c0110f0572a980b599e2417b2653b934fbe440"


class Configuration(BaseModel):
    model_config = ConfigDict(extra="allow", strict=True)
    seed: int = Field(ge=0)
    timesteps: Literal[5000]
    startingAgents: Literal[250]
    startingDiseases: Literal[50]
    headlessMode: Literal[True]
    logfile: str
    agentDecisionModels: list[str] = Field(min_length=1, max_length=1)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("engine", type=Path)
    parser.add_argument("archive", type=Path)
    parser.add_argument("entry")
    parser.add_argument("output", type=Path)
    parser.add_argument("--seconds", type=int, required=True)
    parser.add_argument("--interpreter", type=Path, default=Path(sys.executable))
    args = parser.parse_args()
    assert 1 <= args.seconds <= 1800
    assert not args.output.exists()
    engine = args.engine.resolve()
    interpreter = args.interpreter.resolve(strict=True)
    timeout = shutil.which("timeout")
    assert timeout, "GNU timeout must be installed"
    assert hashlib.sha256(args.archive.read_bytes()).hexdigest() == ARCHIVE_SHA256
    pins = json.loads(Path(__file__).with_name("source-sha256.json").read_text())
    actual = {
        p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in engine.glob("*.py")
    }
    assert actual == pins["source_sha256"]
    with zipfile.ZipFile(args.archive) as archive:
        assert args.entry in archive.namelist() and args.entry.endswith(".config")
        original = archive.read(args.entry)
    config = json.loads(original)
    validated = Configuration.model_validate(config)
    assert validated.model_dump() == config
    defaults = json.loads((engine / "config.json").read_text())["sugarscapeOptions"]
    if args.entry[0].isdigit():
        assert config.keys() == defaults.keys() | {"agentDecisionModel"}
        factor = config["agentSelfishnessFactor"]
        assert len(factor) == 2 and factor[0] == factor[1] and 0 <= factor[0] <= 1
        assert config["agentDecisionModels"] == ["none"]
        assert config["agentDecisionModel"] == "benthamHalfLookaheadBinary"
        assert (
            args.entry
            == f"{factor[0]}-benthamHalfLookaheadBinary{validated.seed}.config"
        )
        effective_model = config["agentDecisionModel"]
    else:
        assert config.keys() == defaults.keys()
        effective_model = validated.agentDecisionModels[0]
        assert effective_model in {
            "rawSugarscape",
            "altruisticHalfLookaheadBinary",
            "benthamHalfLookaheadBinary",
            "egoisticHalfLookaheadBinary",
        }
        assert args.entry == f"{effective_model}{validated.seed}.config"
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    (output / "original.config").write_bytes(original)
    config["logfile"] = str(output / "trajectory.json")
    config_path = output / "config.json"
    config_path.write_text(json.dumps(config, indent=2) + "\n")
    command = [
        timeout,
        "--kill-after=10s",
        f"{args.seconds}s",
        str(interpreter),
        str(engine / "sugarscape.py"),
        "--conf",
        str(config_path),
    ]
    manifest = {
        "release": pins["release"],
        "source_sha256": actual,
        "archive_sha256": ARCHIVE_SHA256,
        "entry": args.entry,
        "seed": validated.seed,
        "original_config_sha256": hashlib.sha256(original).hexdigest(),
        "config_sha256": hashlib.sha256(config_path.read_bytes()).hexdigest(),
        "only_changed_field": "logfile",
        "effective_model": effective_model,
        "command": command,
        "seconds": args.seconds,
        "kill_grace_seconds": 10,
        "pythonhashseed": "0",
        "interpreter_sha256": hashlib.sha256(interpreter.read_bytes()).hexdigest(),
        "python_version": subprocess.check_output(
            [str(interpreter), "-c", "import sys; print(sys.version)"], text=True
        ).strip(),
    }
    (output / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    started = time.monotonic()
    with (
        (output / "stdout.log").open("x") as stdout,
        (output / "stderr.log").open("x") as stderr,
    ):
        process = subprocess.run(
            command,
            cwd=engine,
            env={**os.environ, "PYTHONHASHSEED": "0", "PYTHONDONTWRITEBYTECODE": "1"},
            stdout=stdout,
            stderr=stderr,
        )
    terminal = {
        "exit_code": process.returncode,
        "elapsed_seconds": time.monotonic() - started,
    }
    (output / "terminal.json").write_text(json.dumps(terminal, indent=2) + "\n")
    if process.returncode != 0:
        raise SystemExit(process.returncode)
    raw = (output / "trajectory.json").read_bytes()
    records = json.loads(raw)
    assert 1 <= len(records) <= 5001 and records[0]["population"] == 250
    array_metrics = {"agentWealths", "agentTimesToLive", "agentTimesToLiveAgeLimited"}
    for t, row in enumerate(records):
        assert row["timestep"] == t and row["seed"] == validated.seed
        assert (
            0 <= row["population"] <= 2500
            and int(row["population"]) == row["population"]
        )
        assert {
            key for key, value in row.items() if isinstance(value, list)
        } == array_metrics
        assert all(
            math.isfinite(value)
            for key, value in row.items()
            if key not in array_metrics
        )
        assert all(math.isfinite(value) for key in array_metrics for value in row[key])
    assert records[-1]["timestep"] == 5000 or records[-1]["population"] == 0
    population = records[-1]["population"]
    result = {
        "status": "complete",
        "entry": args.entry,
        "seed": validated.seed,
        "observations": len(records),
        "final_timestep": records[-1]["timestep"],
        "final_population": population,
        "outcome": "extinct"
        if population == 0
        else "below_initial"
        if population < 250
        else "equal_initial"
        if population == 250
        else "above_initial",
        "trajectory_sha256": hashlib.sha256(raw).hexdigest(),
        "elapsed_seconds": terminal["elapsed_seconds"],
    }
    (output / "result.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result))


if __name__ == "__main__":
    main()
