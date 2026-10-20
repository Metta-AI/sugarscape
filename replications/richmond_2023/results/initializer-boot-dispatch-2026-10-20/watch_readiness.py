from pathlib import Path
import json
import subprocess
import time

root = Path(__file__).resolve().parent
node = "relh-sugarscape-richmond-h100-20261017-v1"
started = json.loads((root / "registered-at.json").read_text())["started_unix"]
provisioning_started = 0
while True:
    state = json.loads(
        subprocess.check_output(
            ["autor", "node", "get", node, "--json"], text=True, timeout=30
        )
    )
    assert state["yours"] and state["rate"]["node_per_min_usd_micros"] <= 84000
    with (root / "readiness.jsonl").open("a") as f:
        f.write(json.dumps({"unix": time.time(), "status": state["status"]}) + "\n")
    if state["status"].startswith("running"):
        (root / "node-ready.json").write_text(json.dumps(state, indent=2) + "\n")
        break
    if state["status"].startswith("stopped"):
        (root / "stopped-before-start.json").write_text(
            json.dumps(state, indent=2) + "\n"
        )
        break
    if state["status"] != "queued" and provisioning_started == 0:
        provisioning_started = time.time()
    if time.time() - started > 14400 or (
        provisioning_started and time.time() - provisioning_started > 900
    ):
        commands = json.loads(
            subprocess.check_output(
                ["autor", "ps", node, "--json"], text=True, timeout=30
            )
        )
        assert not any(x["state"] == "running" for x in commands["items"])
        result = subprocess.run(
            ["autor", "node", "stop", node, "--json"],
            capture_output=True,
            text=True,
            timeout=60,
        )
        (root / "readiness-bound-stop.json").write_text(
            json.dumps(
                {
                    "exit_code": result.returncode,
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                },
                indent=2,
            )
            + "\n"
        )
        assert result.returncode == 0
        break
    time.sleep(30)
