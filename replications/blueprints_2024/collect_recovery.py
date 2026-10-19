"""Copy sealed checkpoints from one owned provider command to local storage."""

import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import time

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("node")
parser.add_argument("command")
parser.add_argument("output", type=Path)
parser.add_argument("--seconds", type=int, default=86400)
args = parser.parse_args()
assert 0 < args.seconds <= 86400
args.output.mkdir(parents=True, exist_ok=False)
started = time.monotonic()
received = set()
with (args.output / "polls.jsonl").open("x") as polls:
    while time.monotonic() - started < args.seconds:
        states = json.loads(
            subprocess.check_output(["autor", "ps", args.node, "--json"], text=True)
        )
        state = next(
            row for row in states["items"] if row["command_id"] == args.command
        )
        logs = subprocess.run(
            ["autor", "logs", args.node, args.command], capture_output=True, text=True
        )
        receipts = [
            json.loads(line.removeprefix("SNAPSHOT "))
            for line in logs.stdout.splitlines()
            if line.startswith("SNAPSHOT ")
        ]
        for receipt in receipts:
            name = Path(receipt["archive"]).name
            assert name.startswith("checkpoint-") and name.endswith(".tar.gz")
            if name in received:
                continue
            assert shutil.disk_usage(args.output).free >= receipt["bytes"] + 4 * 1024**3
            target = args.output / name
            assert not target.exists()
            subprocess.run(
                ["autor", "cp", f"{args.node}:{receipt['archive']}", str(target)],
                check=True,
            )
            assert target.stat().st_size == receipt["bytes"]
            with target.open("rb") as stream:
                assert (
                    hashlib.file_digest(stream, "sha256").hexdigest()
                    == receipt["sha256"]
                )
            target.with_suffix(".receipt.json").write_text(
                json.dumps(receipt, indent=2) + "\n"
            )
            received.add(name)
            print(
                json.dumps({"downloaded": name, "counts": receipt["counts"]}),
                flush=True,
            )
        polls.write(
            json.dumps(
                {
                    "state": state,
                    "log_exit_code": logs.returncode,
                    "producer_stdout": logs.stdout,
                    "producer_stderr": logs.stderr,
                    "downloaded": sorted(received),
                    "unix": time.time(),
                }
            )
            + "\n"
        )
        polls.flush()
        if state["state"] in ["exited", "lost"]:
            (args.output / "terminal.json").write_text(
                json.dumps(state, indent=2) + "\n"
            )
            break
        time.sleep(60)
    else:
        raise TimeoutError(
            "Collector deadline reached; inspect the unchanged native command before continuing."
        )
