from pathlib import Path
import json
import subprocess
import time

root = Path(__file__).resolve().parent
node = "relh-sugarscape-baseline-recovery-cpu8-20261019-v1"
command = "cmd-mqy6i"
deadline = time.monotonic() + 1900
while True:
    states = json.loads(subprocess.check_output(["autor", "ps", node, "--json"]))
    state = next(row for row in states["items"] if row["command_id"] == command)
    if state["state"] != "pending_wake":
        break
    assert time.monotonic() < deadline, "Pending command unchanged; inspect queue before further action"
    time.sleep(20)
with (root / "collector.log").open("x") as stream:
    process = subprocess.run([
        "/Users/relh/Code/workspace/sugarscape-replications/.venv/bin/python",
        str(root.parent / "storage-handoff-20261017-001/collect_storage_api_bounded.py"),
        node, command, root.name,
        "--seconds", "24000", "--max-bytes", str(2 * 1024**3)
    ], stdout=stream, stderr=subprocess.STDOUT, timeout=24200)
(root / "collection-terminal.json").write_text(json.dumps({"exit_code": process.returncode}) + "\n")
assert process.returncode == 0
