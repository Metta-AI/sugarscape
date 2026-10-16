"""Run the declared 150-condition reconstruction with a frozen copy of its runner."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("archive", type=Path)
parser.add_argument("java_home", type=Path)
parser.add_argument("output", type=Path)
args = parser.parse_args()
output = args.output.resolve()
output.mkdir(parents=True, exist_ok=False)
runner = output / "runner"
runner.mkdir()
for name in ("run_pilot.py", "Replay.java", "ReplicationRandom.java"):
    shutil.copy2(Path(__file__).with_name(name), runner / name)
protocol = {
    "protocols": ["paper-com0", "paper-com1", "paper-com2"],
    "thresholds": list(range(5)), "seeds": list(range(10)), "cycles": 2000,
    "runs": 150, "historical_seeds_known": False, "unpaced": True,
    "source": "https://www.jasss.org/8/1/2.html",
    "horizon_evidence": "Published Figure4 CT4 population axis ends at2000; apply common2000-cycle horizon across conditions.",
    "scope": "Declared reconstruction. All runs, extinctions, and failed commands retained. Pilot seed0 already observed; no claim of blinded validation.",
    "comparisons": ["survival and extinction timing by protocol and threshold", "population, talk, and listen trajectories", "shared harvest events / all harvest events", "shared consumer participations / all consumer participations", "native cooperating-agent average retained separately"],
    "undefined_ratios": "No eating events gives undefined cooperation ratios; empty-population native gene zeros are not observed preferences.",
    "runner_sha256": {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in runner.iterdir()},
}
(output / "protocol.json").write_text(json.dumps(protocol, indent=2) + "\n")
with (output / "completed.jsonl").open("x") as ledger:
    for model in protocol["protocols"]:
        for threshold in protocol["thresholds"]:
            for seed in protocol["seeds"]:
                name = f"{model}-ct{threshold}-seed{seed}"
                command = [sys.executable, str(runner / "run_pilot.py"), str(args.archive.resolve()),
                           str(args.java_home.resolve()), str(output / name), model, str(seed),
                           "--threshold", str(threshold), "--cycles", str(protocol["cycles"]), "--unpaced"]
                with (output / (name + ".log")).open("x") as log:
                    result = subprocess.run(command, stdout=log, stderr=subprocess.STDOUT)
                record = {"name": name, "command": command, "exit_code": result.returncode}
                ledger.write(json.dumps(record) + "\n")
                ledger.flush()
                print(json.dumps(record), flush=True)
                assert result.returncode == 0, name
(output / "exit.json").write_text(json.dumps({"exit_code": 0, "completed_runs": 150}) + "\n")
