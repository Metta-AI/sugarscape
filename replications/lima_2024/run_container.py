"""Run the prepared author container scenario with a one-hour bound."""

import argparse
from pathlib import Path
import json
import subprocess
import time

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("run", type=Path)
args = parser.parse_args()
root = args.run.resolve()
project = json.loads((root / "compose.json").read_text())["name"]
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
try:
    with (root / "up.log").open("x") as stream:
        subprocess.run(
            [*compose, "up", "-d", "--no-build"],
            stdout=stream,
            stderr=subprocess.STDOUT,
            check=True,
            timeout=180,
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
            if failed or (
                len(models) == 2 and all(s["State"] == "exited" for s in models)
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
