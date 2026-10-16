"""Run the declared fixed-society ensemble through the compiled simulator."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import time

from pydantic import BaseModel
from typing import Literal


class Experiment(BaseModel):
    scenario: Literal["low-fertility", "birth-cost"]
    first_seed: Literal[1] = 1
    last_seed: Literal[100] = 100
    cycles: Literal[100000] = 100000


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("binary", type=Path)
    parser.add_argument("scenario", choices=["low-fertility", "birth-cost"])
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    experiment = Experiment(scenario=args.scenario)
    binary = args.binary.resolve()
    args.output.mkdir(parents=True, exist_ok=False)
    parameters = (85, 0) if experiment.scenario == "low-fertility" else (10, 40)
    manifest = {"experiment": experiment.model_dump(), "binary_sha256": hashlib.sha256(binary.read_bytes()).hexdigest(),
                "parameters": {"infertility": parameters[0], "birth_cost": parameters[1]},
                "interpretation": "Specification-based ensemble; unresolved source semantics remain explicit."}
    (args.output / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    with (args.output / "completed.jsonl").open("x") as completed:
        for seed in range(experiment.first_seed, experiment.last_seed + 1):
            started = time.monotonic()
            trajectory = args.output / f"seed-{seed}.csv"
            observations = args.output / f"seed-{seed}-observations.csv"
            command = [str(binary), str(seed), *(str(value) for value in parameters), str(experiment.cycles), "100", str(observations.resolve())]
            with trajectory.open("x") as stdout, (args.output / f"seed-{seed}.stderr").open("x") as stderr:
                subprocess.run(command, stdout=stdout, stderr=stderr, check=True)
            record = {"seed": seed, "command": command, "elapsed_seconds": time.monotonic() - started,
                      "trajectory_sha256": hashlib.sha256(trajectory.read_bytes()).hexdigest(),
                      "observations_sha256": hashlib.sha256(observations.read_bytes()).hexdigest()}
            completed.write(json.dumps(record) + "\n")
            completed.flush()
            print(f"Completed {experiment.scenario} seed {seed}", flush=True)


if __name__ == "__main__":
    main()
