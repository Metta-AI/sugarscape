"""Export sealed task artifacts directly to bounded task-owned object storage."""

import argparse
import json
import subprocess
import time
import shlex
from pathlib import Path

p = argparse.ArgumentParser(description=__doc__)
p.add_argument("node")
p.add_argument("command")
p.add_argument("prefix")
p.add_argument("--terminal-file")
p.add_argument("--seconds", type=int, required=True)
p.add_argument("--max-bytes", type=int, required=True)
a = p.parse_args()
assert 0 < a.seconds <= 43200 and 0 < a.max_bytes <= 2 * 1024**3
root = Path(__file__).parent / a.prefix
root.mkdir(exist_ok=False)
started = time.monotonic()
received = set()
total = 0
with (root / "polls.jsonl").open("x") as log:
    while time.monotonic() - started < a.seconds:
        states = json.loads(
            subprocess.check_output(["autor", "--json", "ps", a.node], text=True)
        )
        state = next(s for s in states["items"] if s["command_id"] == a.command)
        ended = state["state"] in ["exited", "lost"]
        receipts = []
        if a.terminal_file:
            if ended:
                assert state["state"] == "exited"
                path = shlex.quote(a.terminal_file)
                metadata = json.loads(
                    subprocess.check_output(
                        [
                            "autor",
                            "--json",
                            "run",
                            a.node,
                            "--timeout",
                            "30",
                            "--",
                            "sh",
                            "-c",
                            f"stat -c %s {path} && sha256sum {path}",
                        ],
                        text=True,
                    )
                )
                assert metadata["exit_code"] == 0 and not metadata["truncated"]
                lines = metadata["stdout"].splitlines()
                receipts = [
                    {
                        "archive": a.terminal_file,
                        "bytes": int(lines[0]),
                        "sha256": lines[1].split()[0],
                    }
                ]
        else:
            offset = 0
            chunks = []
            page_count = 0
            while True:
                for attempt in range(3):
                    observed = subprocess.run(
                        [
                            "autor",
                            "--json",
                            "api",
                            "get",
                            f"/nodes/{a.node}/commands/{a.command}?offset={offset}",
                        ],
                        capture_output=True,
                        text=True,
                        timeout=45,
                    )
                    if observed.returncode == 0:
                        break
                    with (root / "log-read-errors.jsonl").open("a") as errors:
                        errors.write(
                            json.dumps(
                                {
                                    "unix": time.time(),
                                    "offset": offset,
                                    "attempt": attempt + 1,
                                    "exit_code": observed.returncode,
                                    "stdout": observed.stdout,
                                    "stderr": observed.stderr,
                                }
                            )
                            + "\n"
                        )
                    assert attempt < 2, (
                        "Three failed read-only log observations; producer is not restarted"
                    )
                    time.sleep(20)
                output = json.loads(observed.stdout)
                chunks.append(output["output"])
                page_count += 1
                assert offset <= output["next_offset"] <= 8 * 1024**2, (
                    "Bounded command-log read exceeded8MiB"
                )
                if not output["truncated"]:
                    break
                assert output["next_offset"] > offset, (
                    "Truncated response did not advance byte offset"
                )
                offset = output["next_offset"]
            complete_output = "".join(chunks)
            receipts = [
                json.loads(line.removeprefix("SNAPSHOT "))
                for line in complete_output.splitlines()
                if line.startswith("SNAPSHOT ")
            ]
            with (root / "page-observations.jsonl").open("a") as pages:
                pages.write(
                    json.dumps(
                        {
                            "unix": time.time(),
                            "pages": page_count,
                            "next_offset": output["next_offset"],
                            "snapshot_count": len(receipts),
                            "status": output["status"],
                        }
                    )
                    + "\n"
                )
        for receipt in receipts:
            name = Path(receipt["archive"]).name
            assert name.endswith(".tar.gz") and receipt["archive"].startswith(
                ("/root/sugarscape/", "/home/dev/sugarscape/")
            )
            if name in received:
                continue
            total += receipt["bytes"]
            assert total <= a.max_bytes
            destination = a.prefix + "/" + name
            intent = {
                "node": a.node,
                "command": a.command,
                "receipt": receipt,
                "destination": destination,
                "cumulative_bytes": total,
            }
            (root / (name + ".intent.json")).write_text(
                json.dumps(intent, indent=2) + "\n"
            )
            result = json.loads(
                subprocess.check_output(
                    [
                        "autor",
                        "--json",
                        "export",
                        a.node,
                        "--connection",
                        "storage/relh-sugarscape-evidence-20261017",
                        "--source",
                        receipt["archive"],
                        "--dest",
                        destination,
                        "--mission",
                        "relh-sugarscape-replications",
                    ],
                    text=True,
                )
            )
            (root / (name + ".submission.json")).write_text(
                json.dumps(result, indent=2) + "\n"
            )
            export_started = time.monotonic()
            while True:
                status = json.loads(
                    subprocess.check_output(
                        [
                            "autor",
                            "--json",
                            "api",
                            "get",
                            f"/nodes/{a.node}/data-exports/{result['export_id']}",
                        ],
                        text=True,
                    )
                )
                (root / (name + ".status.json")).write_text(
                    json.dumps(status, indent=2) + "\n"
                )
                if status["status"] == "complete":
                    assert status["bytes_transferred"] == receipt["bytes"]
                    break
                assert (
                    status["status"] == "running"
                    and time.monotonic() - export_started < 1800
                )
                time.sleep(10)
            received.add(name)
            print(
                json.dumps(
                    {
                        "stored": destination,
                        "sha256": receipt["sha256"],
                        "bytes": receipt["bytes"],
                    }
                ),
                flush=True,
            )
        log.write(
            json.dumps(
                {
                    "unix": time.time(),
                    "state": state,
                    "stored": sorted(received),
                    "total_bytes": total,
                }
            )
            + "\n"
        )
        log.flush()
        if ended:
            (root / "terminal.json").write_text(json.dumps(state, indent=2) + "\n")
            break
        time.sleep(60)
    else:
        raise TimeoutError(
            "Storage collector deadline; inspect unchanged producer before continuing"
        )
