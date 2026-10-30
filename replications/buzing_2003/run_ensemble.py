"""Run a frozen, explicitly policy-uncertain 2003 reconstruction grid."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("reference_run", type=Path)
parser.add_argument("output", type=Path)
args = parser.parse_args()
output = args.output.resolve()
output.mkdir(parents=True, exist_ok=False)
runner = output / "runner"
(runner / "buzing_2003").mkdir(parents=True)
(runner / "buzing_2005").mkdir()
shutil.copy2(Path(__file__).with_name("run_pilot.py"), runner / "buzing_2003/run_pilot.py")
shutil.copy2(Path(__file__).resolve().parent.parent / "buzing_2005/Replay.java", runner / "buzing_2005/Replay.java")
shutil.copy2(Path(__file__).with_name("specification.json"), output / "specification.json")
reference = args.reference_run.resolve()
protocol = {"study": "Buzing2003", "policies": ["none", "read", "response", "expiry-one"],
            "thresholds": list(range(5)), "seeds": list(range(10)), "cycles": 500, "runs": 200,
            "reference_run": str(reference), "reference_manifest_sha256": hashlib.sha256((reference / "manifest.json").read_bytes()).hexdigest(),
            "runner_sha256": {str(p.relative_to(runner)): hashlib.sha256(p.read_bytes()).hexdigest() for p in runner.rglob('*') if p.is_file()},
            "policy_uncertainty": "Three communicating removal policies are declared alternatives because the inspected paper does not pin one. Do not select one after seeing agreement and call it historical replication.",
            "pilot_disclosure": "Seed0threshold1 pilots for all four policies observed; all extinct. Response repeated exactly. Full grid fixed before other outcomes.",
            "comparisons": "Ten independent seeds per policy/threshold; full500cycle trajectories, survival, population variability, cooperation denominators, fixed listening and evolving talk. No automatic paper-level verdict."}
(output / "protocol.json").write_text(json.dumps(protocol, indent=2) + "\n")
completed = 0
for policy in protocol["policies"]:
    for threshold in protocol["thresholds"]:
        for seed in protocol["seeds"]:
            name = f"{policy}-ct{threshold}-seed{seed}"
            command = [sys.executable, str(runner / "buzing_2003/run_pilot.py"), str(reference), str(output / name), policy, str(threshold), str(seed)]
            with (output / (name + ".log")).open("w") as log:
                result = subprocess.run(command, stdout=log, stderr=subprocess.STDOUT)
            with (output / "completed.jsonl").open("a") as ledger:
                ledger.write(json.dumps({"name": name, "command": command, "exit_code": result.returncode}) + "\n")
                ledger.flush()
            if result.returncode != 0:
                (output / "exit.json").write_text(json.dumps({"exit_code": result.returncode, "completed_runs": completed}) + "\n")
                sys.exit(result.returncode)
            completed += 1
(output / "exit.json").write_text(json.dumps({"exit_code": 0, "completed_runs": completed}) + "\n")
