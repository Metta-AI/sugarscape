"""Run either prepared author scenario with a one-hour bound."""

import argparse
from contextlib import ExitStack
import os
from pathlib import Path
import json
import signal
import subprocess
import time

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("run", type=Path)
parser.add_argument("--host", action="store_true")
args = parser.parse_args()
root = args.run.resolve()
config = json.loads((root / "compose.json").read_text())
project = config["name"]
assert ("jacamo" not in config["services"]) == args.host
existing = subprocess.run(
    [
        "docker",
        "ps",
        "-a",
        "--filter",
        f"label=com.docker.compose.project={project}",
        "--format",
        "{{.ID}}",
    ],
    capture_output=True,
    text=True,
    check=True,
)
assert not existing.stdout.strip(), (
    "Use a fresh project; never restart completed evidence"
)
compose = ["docker", "compose", "-f", str(root / "compose.json")]
assert not (root / "launch.json").exists()
started = time.time()
(root / "launch.json").write_text(
    json.dumps({"unix": started, "deadline_seconds": 3600, "project": project}) + "\n"
)
host_processes = []
host_logs = ExitStack()
try:
    with (root / "up.log").open("x") as stream:
        subprocess.run(
            [*compose, "up", "-d", "--no-build"],
            stdout=stream,
            stderr=subprocess.STDOUT,
            check=True,
            timeout=180,
        )
    if args.host:
        runtime = json.loads((root / "runtime.json").read_text())
        env = os.environ.copy()
        env.update(
            JAVA_HOME=runtime["java_home"],
            GRADLE_USER_HOME=runtime["gradle_cache"],
            JAVA_TOOL_OPTIONS="-Xmx512m",
            host="127.0.0.1",
        )
        host_log = host_logs.enter_context((root / "jacamo-host.log").open("x"))
        process = subprocess.Popen(
            [
                runtime["gradle_home"] + "/bin/gradle",
                "--no-daemon",
                "--no-watch-fs",
                "--console=plain",
                "run",
            ],
            cwd=root / "shared_volume/jacamo/jacamo_model",
            env=env,
            stdout=host_log,
            stderr=subprocess.STDOUT,
            start_new_session=True,
        )
        host_processes.append(process)
        (root / "host-launch.json").write_text(
            json.dumps({"pid": process.pid, "unix": time.time()}) + "\n"
        )
    with (root / "states.jsonl").open("x") as stream:
        while time.time() - started < 3600:
            result = subprocess.run(
                [*compose, "ps", "-a", "--format", "json"],
                capture_output=True,
                text=True,
                check=True,
                timeout=30,
            )
            states = [json.loads(line) for line in result.stdout.splitlines()]
            stream.write(json.dumps({"unix": time.time(), "states": states}) + "\n")
            stream.flush()
            failed = [
                s
                for s in states
                if s["Service"] != "clear_files"
                and s["State"] == "exited"
                and s["ExitCode"] != 0
            ]
            models = [s for s in states if s["Service"] in ["modelo_1", "modelo_2"]]
            if (
                any(process.poll() is not None for process in host_processes)
                or failed
                or (len(models) == 2 and all(s["State"] == "exited" for s in models))
            ):
                (root / "observed-stop.json").write_text(
                    json.dumps({"failed": failed, "models": models}, indent=2) + "\n"
                )
                break
            time.sleep(15)
        else:
            (root / "deadline.json").write_text(
                json.dumps({"elapsed": time.time() - started}) + "\n"
            )
finally:
    for process in host_processes:
        if process.poll() is None:
            os.killpg(process.pid, signal.SIGTERM)
            process.wait(timeout=30)
    host_logs.close()
    with (root / "stop.log").open("x") as stream:
        subprocess.run(
            [*compose, "stop", "--timeout", "20"],
            stdout=stream,
            stderr=subprocess.STDOUT,
            check=True,
            timeout=120,
        )
    with (root / "native.log").open("x") as stream:
        subprocess.run(
            [*compose, "logs", "--no-color", "--timestamps"],
            stdout=stream,
            stderr=subprocess.STDOUT,
            check=True,
            timeout=60,
        )
    result = subprocess.run(
        [*compose, "ps", "-a", "--format", "json"],
        capture_output=True,
        text=True,
        check=True,
        timeout=30,
    )
    (root / "terminal-containers.jsonl").write_text(result.stdout)
    assert all(
        json.loads(line)["State"] == "exited" for line in result.stdout.splitlines()
    )
    (root / "terminal.json").write_text(
        json.dumps({"elapsed": time.time() - started, "containers_stopped": True})
        + "\n"
    )
