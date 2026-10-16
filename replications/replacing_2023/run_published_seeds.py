"""Replay every Table 3 seed without filtering or assigning qualitative verdicts."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("engine", type=Path)
parser.add_argument("scenario", choices=["seasonal_migration", "reproduction_limited", "disease_basic"])
parser.add_argument("output", type=Path)
args = parser.parse_args()
root = Path(__file__).resolve().parent
target_path = root / "published_targets.json"
targets = json.loads(target_path.read_text())
seeds = [row["seed"] for row in targets["table3"]]
assert len(seeds) == len(set(seeds)) == 20
args.output.mkdir(parents=True, exist_ok=False)
output = args.output.resolve()
manifest = {"scenario": args.scenario, "seeds": seeds, "engine": str(args.engine.resolve()),
            "revision": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=args.engine, text=True).strip(),
            "runner_sha256": hashlib.sha256((root / "run.py").read_bytes()).hexdigest(),
            "target_sha256": hashlib.sha256(target_path.read_bytes()).hexdigest(),
            "interpretation": "Complete published seed set. No post-hoc exclusions or numerical qualitative-similarity thresholds."}
(output / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
with (output / "completed.jsonl").open("x") as completed:
    for seed in seeds:
        assert hashlib.sha256((root / "run.py").read_bytes()).hexdigest() == manifest["runner_sha256"]
        run = output / f"seed-{seed}"
        command = [sys.executable, str(root / "run.py"), str(args.engine.resolve()), args.scenario, str(seed), str(run)]
        with (output / f"seed-{seed}.log").open("x") as log:
            subprocess.run(command, stdout=log, stderr=subprocess.STDOUT, check=True)
        result = json.loads((run / "result.json").read_text())
        completed.write(json.dumps({"seed": seed, "command": command, "result": result}) + "\n")
        completed.flush()
        print(json.dumps({"seed": seed, "result": result}), flush=True)
