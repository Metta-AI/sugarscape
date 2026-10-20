"""Dispatch this one prepared task within its startup allowance; never duplicate a launch."""

import hashlib
import json
import shlex
from pathlib import Path
import subprocess
import time

root = Path(__file__).resolve().parent
node = "relh-sugarscape-richmond-h100-20261017-v1"
assert not (root / "launch.json").exists()
clock = json.loads((root / "startup-clock.json").read_text())
while True:
    state = json.loads(
        subprocess.check_output(
            ["autor", "node", "get", node, "--json"], text=True, timeout=60
        )
    )
    assert state["yours"] and state["rate"]["node_per_min_usd_micros"] <= 84000
    (root / "readiness.json").write_text(json.dumps(state, indent=2) + "\n")
    if state["status"].startswith("running"):
        break
    if time.time() - clock["started_unix"] >= clock["maximum_ready_seconds"]:
        result = subprocess.run(
            ["autor", "node", "stop", node, "--json"],
            capture_output=True,
            text=True,
            timeout=60,
        )
        (root / "startup-bound-stop.json").write_text(
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
        raise SystemExit(
            "Startup bound reached; task-owned node stopped without simulation."
        )
    time.sleep(20)
commands = json.loads(
    subprocess.check_output(["autor", "ps", node, "--json"], text=True, timeout=60)
)
assert not any(item["state"] == "running" for item in commands["items"])
archive = root / "input.tar.gz"
result = subprocess.run(
    [
        "autor",
        "cp",
        str(archive),
        node
        + ":/root/sugarscape/richmond-initializer-native-controls-input-001.tar.gz",
        "--json",
    ],
    capture_output=True,
    text=True,
    timeout=120,
)
(root / "ready-upload.json").write_text(
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
assert result.returncode == 0, result.stderr
code = "\n".join(
    [
        "from pathlib import Path",
        "import hashlib,tarfile,os",
        "archive=Path('/root/sugarscape/richmond-initializer-native-controls-input-001.tar.gz')",
        "assert hashlib.sha256(archive.read_bytes()).hexdigest()=="
        + repr(hashlib.sha256(archive.read_bytes()).hexdigest()),
        "root=Path('/root/sugarscape/richmond-initializer-native-controls-001')",
        "root.mkdir()",
        "with tarfile.open(archive) as bundle:",
        "    assert all(m.isfile() or m.isdir() for m in bundle.getmembers())",
        "    assert all(not Path(m.name).is_absolute() and '..' not in Path(m.name).parts for m in bundle.getmembers())",
        "    bundle.extractall(root)",
        "os.execv('/usr/bin/python3',['/usr/bin/python3',str(root/'run_controls.py')])",
    ]
)
result = subprocess.run(
    [
        "autor",
        "run",
        node,
        "-d",
        "--json",
        "--",
        "/usr/bin/timeout",
        "--kill-after=30",
        "3600",
        "/bin/bash",
        "-c",
        "set -eu; export DEBIAN_FRONTEND=noninteractive; apt-get update -qq; apt-get install -y -qq python3 git cmake; exec /usr/bin/python3 -c "
        + shlex.quote(code),
    ],
    capture_output=True,
    text=True,
    timeout=60,
)
(root / "launch.json").write_text(
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
assert result.returncode == 0, result.stderr
print("Launched", json.loads(result.stdout)["command_id"], flush=True)
