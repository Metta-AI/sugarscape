"""Bound the observer and verify native-log parity plus all original report fields."""
from pathlib import Path
import gzip
import hashlib
import json
import os
import subprocess
import sys
import time

root = Path(__file__).resolve().parent
base = root.parent.parent
previous = root.parent / "replacing-trade-long-horizon-001"
assert json.loads((previous / "qualification-failure.json").read_bytes())["qualification_exit_code"] == 1
start = time.monotonic()
command = [sys.executable, str(root / "observe.py")]
with (root / "stdout.log").open("x") as stdout, (root / "stderr.log").open("x") as stderr:
    result = subprocess.run(command, cwd=base / "sugarscape-dtl-replacing-reference", env={**os.environ, "PYTHONHASHSEED": "0", "PYTHONDONTWRITEBYTECODE": "1"}, stdout=stdout, stderr=stderr, timeout=900)
(root / "exit.json").write_text(json.dumps({"exit_code": result.returncode, "elapsed_seconds": time.monotonic() - start, "command": command}, indent=2) + "\n")
assert result.returncode == 0
native = (previous / "seed-14133/spice_growback/trajectory.json").read_bytes()
observed = (root / "trajectory.json").read_bytes()
assert observed == native
original_path = base / "sugarscape-replacing/replications/replacing_2023/results/trade-lending-paired20-2026-10-15/seed-14133/spice_growback/trajectory.json.gz"
original = json.loads(gzip.decompress(original_path.read_bytes()))
reconstructed = [json.loads(line) for line in (root / "original-schedule.jsonl").read_text().splitlines()]
assert reconstructed == original and len(original) == 501
m = json.loads((root / "manifest.json").read_bytes())
assert hashlib.sha256((root / "observe.py").read_bytes()).hexdigest() == m["observer_sha256"]
assert all(hashlib.sha256((base / "sugarscape-dtl-replacing-reference" / name).read_bytes()).hexdigest() == digest for name, digest in m["source_sha256"].items())
report = {"native_trajectory_byte_exact": True, "native_observations": len(json.loads(native)), "original_schedule_all_fields_exact": True, "original_observations": len(original), "native_trajectory_sha256": hashlib.sha256(native).hexdigest(), "original_schedule_sha256": hashlib.sha256((root / "original-schedule.jsonl").read_bytes()).hexdigest(), "scope": "Baseline seed14133 only. Passive reporting preserves the full native10000step log and reconstructs every original500step field. Does not establish equilibrium or complete the trade/lending ensemble."}
(root / "audit.json").write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps(report), flush=True)
