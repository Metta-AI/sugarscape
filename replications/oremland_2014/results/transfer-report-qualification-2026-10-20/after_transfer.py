"""Run independent R reporting only after all production transfers pass audit."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import time

root = Path(__file__).resolve().parent
plan = json.loads((root / "plan.json").read_bytes())
for name, digest in plan["source_sha256"].items():
    assert hashlib.sha256((root / name).read_bytes()).hexdigest() == digest
campaign = Path(plan["campaign"])
deadline = time.monotonic() + plan["observation_seconds"]
while True:
    status = subprocess.run(["ps", "-p", str(plan["transfer_watcher_pid"]), "-o", "stat="], capture_output=True, text=True, timeout=10)
    assert status.returncode in [0, 1]
    if status.returncode == 1 or status.stdout.strip().startswith("Z"):
        break
    assert time.monotonic() < deadline
    time.sleep(60)
assert json.loads((campaign / "transfer-audit-terminal.json").read_bytes())["exit_code"] == 0
transfer_plan = json.loads((campaign / "transfer/plan.json").read_bytes())
assert len(transfer_plan["groups"]) == 18
assert {(g["width"], g["optimizer_seed"]) for g in transfer_plan["groups"]} == {
    (width, seed) for width in [50, 40, 30, 20, 10, 5] for seed in [20261021, 20261022, 20261023]
}
for name, digest in plan["source_sha256"].items():
    assert hashlib.sha256((root / name).read_bytes()).hexdigest() == digest
with (root / "production-report.log").open("x") as stream:
    process = subprocess.run(
        ["/opt/homebrew/bin/Rscript", "--vanilla", str(root / "report.R"), str(campaign / "transfer"), str(campaign / "transfer-audit.json"), str(root / "production")],
        stdout=stream, stderr=subprocess.STDOUT,
        env={**os.environ, "R_LIBS_USER": "/Users/relh/Code/workspace/sugarscape-replication-tools/R-library"}, timeout=600,
    )
(root / "terminal.json").write_text(json.dumps({"exit_code": process.returncode, "visual_review_complete": False}, indent=2) + "\n")
assert process.returncode == 0
