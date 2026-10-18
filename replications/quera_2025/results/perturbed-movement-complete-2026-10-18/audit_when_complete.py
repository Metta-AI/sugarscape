import json
import subprocess
import sys
import time
from pathlib import Path

root = Path(__file__).resolve().parent
started = time.monotonic()
while not (root / "exit.json").exists():
    assert time.monotonic() - started < 7500, "Native completion was not recorded within the declared limit"
    time.sleep(5)
terminal = json.loads((root / "exit.json").read_text())
assert terminal["exit_code"] == 0 and terminal["reason"] == "exited", terminal
command = [sys.executable, str(root / "replay_movement.py"), str(root / "native"), str(root.parent / "quera-gradient-ensemble-001"), str(root / "replay"), "--profile", "gradient-trace"]
(root / "audit-command.json").write_text(json.dumps(command, indent=2) + "\n")
with (root / "audit.log").open("x") as log:
    result = subprocess.run(command, stdout=log, stderr=subprocess.STDOUT, timeout=5400, check=True)
report = json.loads((root / "replay/audit.json").read_text())
assert len(report["runs"]) == 9180
summary = {"cases": len(report["runs"]), "agent_updates": sum(r["agent_updates"] for r in report["runs"]), "cell_updates": sum(r["cell_updates"] for r in report["runs"]), "maximum_state_error": max(r["maximum_absolute_state_error"] for r in report["runs"]), "scope": "Seeds4:258 only. Reconcile separately with qualification seed3; no paper-completion claim."}
(root / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
print(json.dumps(summary))
