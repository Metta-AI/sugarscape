"""Launch one bounded batch on the existing idle task-owned CPU node."""

from pathlib import Path
import base64
import hashlib
import json
import shlex
import subprocess

root = Path(__file__).resolve().parent
node = "relh-sugarscape-selfishness037-cpu8-20261018-v1"
assert not (root / "submission.json").exists()
metadata = json.loads(
    subprocess.check_output(
        ["autor", "api", "get", "/nodes/" + node, "--json"], text=True, timeout=60
    )
)
commands = json.loads(
    subprocess.check_output(["autor", "ps", node, "--json"], text=True, timeout=60)
)
(root / "node-before-retry1.json").write_text(json.dumps(metadata, indent=2) + "\n")
(root / "commands-before-retry1.json").write_text(json.dumps(commands, indent=2) + "\n")
assert metadata["id"] == "b787247e-4d63-4f25-b72f-544d5307bbe8"
assert metadata["yours"] and metadata["chip"] == "cpu-8"
assert metadata["status"].startswith("running")
assert metadata["rate"]["node_per_min_usd_micros"] <= 12000
assert metadata["rate"]["idle_window_minutes"] <= 15
assert all(c["state"] in ("exited", "killed", "lost") for c in commands["items"])
payload = (root / "payload.tar.gz").read_bytes()
assert (
    hashlib.sha256(payload).hexdigest()
    == json.loads((root / "payload-readback.json").read_text())["sha256"]
)
remote = "/root/sugarscape/" + root.name
encoded = base64.b64encode(payload).decode()
script = (
    "set -eu\ntest ! -e "
    + shlex.quote(remote)
    + "\nmkdir "
    + shlex.quote(remote)
    + "\ncd "
    + shlex.quote(remote)
    + "\nprintf %s "
    + shlex.quote(encoded)
    + ' | base64 -d > payload.tar.gz\nprintf "%s  payload.tar.gz\\n" '
    + hashlib.sha256(payload).hexdigest()
    + " | sha256sum -c -\ntar -xzf payload.tar.gz\nexec /usr/bin/timeout --kill-after=30s 32340s bash bootstrap.sh\n"
)
(root / "launch-intent-retry1.json").write_text(
    json.dumps(
        {
            "node": node,
            "remote": remote,
            "payload_sha256": hashlib.sha256(payload).hexdigest(),
            "outer_seconds": 32340,
            "kill_grace_seconds": 30,
            "maximum_rate_usd_per_minute": 0.012,
            "conservative_compute_setup_export_idle_ceiling_usd": 7.02,
            "scope": "Exactly400 frozen original inputs with two full native runtime gates; no automatic retries or budget extensions.",
        },
        indent=2,
    )
    + "\n"
)
p = subprocess.run(
    [
        "autor",
        "run",
        node,
        "-d",
        "--timeout",
        "300",
        "--json",
        "--",
        "bash",
        "-lc",
        script,
    ],
    capture_output=True,
    text=True,
    timeout=350,
)
(root / "submission.json").write_text(
    json.dumps(
        {"exit_code": p.returncode, "stdout": p.stdout, "stderr": p.stderr}, indent=2
    )
    + "\n"
)
assert p.returncode == 0, p.stderr
print(p.stdout, flush=True)
