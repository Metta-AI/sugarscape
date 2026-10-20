"""Observe every completed published seed and require native trajectory parity."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("batch", type=Path)
parser.add_argument("output", type=Path)
args = parser.parse_args()
manifest = json.loads((args.batch / "manifest.json").read_text())
completed = [json.loads(line) for line in (args.batch / "completed.jsonl").read_text().splitlines()]
assert [r["seed"] for r in completed] == manifest["seeds"]
assert len(completed) == 20
root = Path(__file__).resolve().parent
sources = {name: hashlib.sha256((root / name).read_bytes()).hexdigest() for name in ["observe.py", "audit_observation.py"]}
args.output.mkdir(parents=True, exist_ok=False)
output = args.output.resolve()
(output / "manifest.json").write_text(json.dumps({"native_batch": str(args.batch.resolve()), "scenario": manifest["scenario"],
    "seeds": manifest["seeds"], "source_sha256": sources, "interpretation": "Complete observational replays; no qualitative paper verdict."}, indent=2) + "\n")
with (output / "completed.jsonl").open("x") as stream:
    for seed in manifest["seeds"]:
        assert all(hashlib.sha256((root / name).read_bytes()).hexdigest() == checksum for name, checksum in sources.items())
        baseline = args.batch.resolve() / f"seed-{seed}"
        observed = output / f"seed-{seed}"
        commands = [[sys.executable, str(root / "observe.py"), manifest["engine"], str(baseline), str(observed)],
                    [sys.executable, str(root / "audit_observation.py"), str(baseline), str(observed)]]
        with (output / f"seed-{seed}.log").open("x") as log:
            for command in commands:
                subprocess.run(command, stdout=log, stderr=subprocess.STDOUT,
                               env={**os.environ, "PYTHONHASHSEED": "0", "PYTHONDONTWRITEBYTECODE": "1"}, check=True)
        result = json.loads((observed / "audit.json").read_text())
        assert result["native_trajectory_byte_identical"]
        stream.write(json.dumps({"seed": seed, "commands": commands, "result": result}) + "\n")
        stream.flush()
        print(json.dumps({"seed": seed, "result": result}), flush=True)
