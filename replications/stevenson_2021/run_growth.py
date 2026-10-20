"""Run the predeclared dense fixed-society growth ensembles."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import time

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("binary", type=Path)
parser.add_argument("output", type=Path)
args = parser.parse_args()
binary = args.binary.resolve()
source = Path(__file__).with_name("simulate.cpp")
protocol = Path(__file__).with_name("GROWTH_PROTOCOL.md")
args.output.mkdir(parents=True, exist_ok=False)
manifest = {
    "binary_sha256": hashlib.sha256(binary.read_bytes()).hexdigest(),
    "source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
    "protocol_sha256": hashlib.sha256(protocol.read_bytes()).hexdigest(),
    "runner_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    "seeds": list(range(1, 101)), "cycles": 3000, "record_every": 1,
    "scenarios": {"low-fertility": [85, 0], "birth-cost": [10, 40]},
    "scope": "Specification-based fixed-society growth diagnostic; author fitting choices unresolved.",
}
(args.output / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
(args.output / "GROWTH_PROTOCOL.md").write_bytes(protocol.read_bytes())
with (args.output / "completed.jsonl").open("x") as completed:
    for scenario, parameters in manifest["scenarios"].items():
        for seed in manifest["seeds"]:
            assert shutil.disk_usage(args.output).free >= 2 * 1024**3
            assert hashlib.sha256(binary.read_bytes()).hexdigest() == manifest["binary_sha256"]
            trajectory = args.output / f"{scenario}-{seed}.csv"
            observations = args.output / f"{scenario}-{seed}-observations.csv"
            command = [str(binary), str(seed), *(str(v) for v in parameters), "3000", "1", str(observations.resolve())]
            started = time.monotonic()
            with trajectory.open("x") as stdout, trajectory.with_suffix(".stderr").open("x") as stderr:
                subprocess.run(command, stdout=stdout, stderr=stderr, check=True)
            record = {"scenario": scenario, "seed": seed, "command": command,
                      "elapsed_seconds": time.monotonic() - started,
                      "trajectory_sha256": hashlib.sha256(trajectory.read_bytes()).hexdigest(),
                      "observations_sha256": hashlib.sha256(observations.read_bytes()).hexdigest()}
            completed.write(json.dumps(record) + "\n")
            completed.flush()
            print(f"Completed {scenario} seed {seed}", flush=True)
