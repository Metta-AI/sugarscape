"""Run a declared seed range using the historical CLI and retain lossless trajectories."""
import argparse
import gzip
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
from typing import Literal

from pydantic import BaseModel, Field


class Batch(BaseModel):
    model: Literal["rawSugarscape", "egoist", "altruist", "bentham"]
    first_seed: int = Field(ge=1, le=501)
    last_seed: int = Field(ge=1, le=501)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("engine", type=Path)
    parser.add_argument("model")
    parser.add_argument("first_seed", type=int)
    parser.add_argument("last_seed", type=int)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    batch = Batch(model=args.model, first_seed=args.first_seed, last_seed=args.last_seed)
    assert batch.first_seed <= batch.last_seed
    assert batch.last_seed <= 500 or batch.first_seed == batch.last_seed == 501
    runner = Path(__file__).with_name("run.py").resolve()
    args.output.mkdir(parents=True, exist_ok=False)
    manifest = {"batch": batch.model_dump(), "runner_sha256": hashlib.sha256(runner.read_bytes()).hexdigest(),
                "batch_runner_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                "scope": "Seeds 1–500 are the declared ensemble; seed 501 is an operational check only."}
    (args.output / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    with (args.output / "completed.jsonl").open("x") as completed:
        for seed in range(batch.first_seed, batch.last_seed + 1):
            assert hashlib.sha256(runner.read_bytes()).hexdigest() == manifest["runner_sha256"]
            assert shutil.disk_usage(args.output).free >= 1024**3, "At least 1 GiB free is required before each run"
            output = args.output / f"seed-{seed}"
            command = [sys.executable, str(runner), str(args.engine.resolve()), "--seed", str(seed),
                       "--model", batch.model, "--output", str(output.resolve())]
            subprocess.run(command, check=True)
            result = json.loads((output / "result.json").read_text())
            trajectory = output / "trajectory.json"
            raw = trajectory.read_bytes()
            assert hashlib.sha256(raw).hexdigest() == result["trajectory_sha256"]
            compressed = trajectory.with_suffix(".json.gz")
            with compressed.open("xb") as stream:
                stream.write(gzip.compress(raw, mtime=0))
            assert gzip.decompress(compressed.read_bytes()) == raw
            # This batch's declared storage format is gzip; preserve every original byte within it.
            trajectory.unlink()
            record = {"seed": seed, "command": command, "result": result,
                      "compressed_sha256": hashlib.sha256(compressed.read_bytes()).hexdigest()}
            completed.write(json.dumps(record) + "\n")
            completed.flush()
            print(f"Archived {batch.model} seed {seed}", flush=True)


if __name__ == "__main__":
    main()
