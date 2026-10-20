"""Render only after the existing predictive analysis has terminated successfully."""
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
    result = subprocess.run(
        ["ps", "-p", str(plan["predictive_watcher_pid"]), "-o", "stat="],
        capture_output=True, text=True, timeout=10,
    )
    assert result.returncode in [0, 1]
    if result.returncode == 1 or result.stdout.strip().startswith("Z"):
        break
    assert time.monotonic() < deadline
    time.sleep(60)
terminal = json.loads((campaign / "predictive-terminal.json").read_bytes())
assert terminal["exit_code"] == 0 and terminal["native_trajectories"] == 4000
assert terminal["python_audit_passed"] and terminal["independent_r_arithmetic_passed"]
for name, digest in plan["source_sha256"].items():
    assert hashlib.sha256((root / name).read_bytes()).hexdigest() == digest
with (root / "render.log").open("x") as stream:
    result = subprocess.run(
        ["/opt/homebrew/bin/Rscript", "--vanilla", str(root / "render.R"), str(campaign), str(root / "figures")],
        stdout=stream, stderr=subprocess.STDOUT,
        env={**os.environ, "R_LIBS_USER": "/Users/relh/Code/workspace/sugarscape-replication-tools/R-library"},
        timeout=180,
    )
(root / "terminal.json").write_text(json.dumps({"exit_code": result.returncode, "visual_review_complete": False}, indent=2) + "\n")
assert result.returncode == 0
