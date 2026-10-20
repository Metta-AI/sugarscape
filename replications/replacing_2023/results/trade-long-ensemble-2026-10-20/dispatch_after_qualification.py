"""Wait for this owned qualification, then dispatch the gated bounded continuation once."""
from pathlib import Path
import json
import subprocess
import sys
import time

root = Path(__file__).resolve().parent
qualification = root.parent / "replacing-trade-passive-qualification-001"
assert not (root / "dispatch.json").exists() and not (root / "ensemble-process.json").exists()
deadline = time.monotonic() + 900
while not (qualification / "audit.json").exists():
    process = subprocess.run(["ps", "-p", "65556", "-o", "command="], capture_output=True, text=True, timeout=10)
    assert process.returncode == 0 and str(qualification / "run_audit.py") in process.stdout, "Qualification stopped without an accepted audit; inspect failure, do not retry automatically"
    assert time.monotonic() < deadline
    time.sleep(15)
audit = json.loads((qualification / "audit.json").read_bytes())
p = json.loads((root / "protocol.json").read_bytes())
assert all(audit[k] == v for k, v in p["qualification_required"].items())
with (root / "ensemble.log").open("x") as log:
    process = subprocess.Popen([sys.executable, str(root / "run.py")], stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
(root / "ensemble-process.json").write_text(json.dumps({"pid": process.pid, "launched_after_qualified_audit": True, "workers": 4, "admission_seconds": 14400, "per_run_seconds": 1800}, indent=2) + "\n")
print(json.dumps({"ensemble_pid": process.pid}), flush=True)
