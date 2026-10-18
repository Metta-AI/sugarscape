"""Run declared original inputs with one owned process group per input."""

import argparse
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import signal
import subprocess
import sys
import time
from typing import IO

from pydantic import BaseModel, ConfigDict, Field


class Plan(BaseModel):
    model_config = ConfigDict(extra="forbid")
    model: str
    indices: list[int]
    workers: int = Field(ge=1, le=32)
    per_input_seconds: float = Field(gt=0)
    total_seconds: float = Field(gt=0)


@dataclass
class Worker:
    index: int
    process: subprocess.Popen
    log: IO[str]
    started: float
    command: list[str]
    stop_reason: str = ""
    term_at: float = 0


def groups() -> set[int]:
    """Exclude zombies: they cannot write and await their parent's reaping."""
    output = subprocess.check_output(["ps", "-eo", "pgid=,stat="], text=True)
    return {
        int(row.split()[0]) for row in output.splitlines() if "Z" not in row.split()[1]
    }


def signal_group(group: int, number: signal.Signals) -> None:
    result = subprocess.run(
        ["kill", "-" + number.name.removeprefix("SIG"), "--", "-" + str(group)],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0 or group not in groups(), result.stderr


parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("engine", type=Path)
parser.add_argument("archive", type=Path)
parser.add_argument("plan", type=Path)
parser.add_argument("output", type=Path)
args = parser.parse_args()
plan = Plan.model_validate_json(args.plan.read_bytes())
assert len(plan.indices) == len(set(plan.indices))
assert all(0 <= i < 500 for i in plan.indices)
args.output.mkdir(parents=True)
(args.output / "plan.json").write_bytes(args.plan.read_bytes())
stop_signal = 0


def request_stop(number: int, frame: object) -> None:
    global stop_signal
    stop_signal = number


signal.signal(signal.SIGTERM, request_stop)
signal.signal(signal.SIGINT, request_stop)
started = time.monotonic()
pending = iter(plan.indices)
workers: list[Worker] = []
owned: list[int] = []
exhausted = False
with (args.output / "attempts.jsonl").open("x") as ledger:
    try:
        while workers or not exhausted:
            now = time.monotonic()
            stopping = bool(stop_signal) or now - started >= plan.total_seconds
            if stopping:
                exhausted = True
            while not exhausted and len(workers) < plan.workers:
                index = next(pending, -1)
                if index == -1:
                    exhausted = True
                    break
                command = [
                    sys.executable,
                    str(Path(__file__).with_name("run_batch.py")),
                    str(args.engine.resolve()),
                    str(args.archive.resolve()),
                    plan.model,
                    str((args.output / f"input-{index}").resolve()),
                    "--start",
                    str(index),
                    "--stop",
                    str(index + 1),
                ]
                log = (args.output / f"input-{index}.log").open("x")
                process = subprocess.Popen(
                    command,
                    stdout=log,
                    stderr=subprocess.STDOUT,
                    start_new_session=True,
                )
                owned.append(process.pid)
                workers.append(Worker(index, process, log, time.monotonic(), command))
            live_groups = groups()
            for worker in workers[:]:
                code = worker.process.poll()
                if code is not None:
                    live_groups = groups()
                if code is not None and worker.process.pid not in live_groups:
                    worker.log.close()
                    record = {
                        "index": worker.index,
                        "command": worker.command,
                        "exit_code": code,
                        "stop_reason": worker.stop_reason,
                        "elapsed_seconds": now - worker.started,
                    }
                    if code == 0:
                        completed = (
                            args.output / f"input-{worker.index}" / "completed.jsonl"
                        )
                        record["completed_ledger_sha256"] = hashlib.sha256(
                            completed.read_bytes()
                        ).hexdigest()
                    ledger.write(json.dumps(record) + "\n")
                    ledger.flush()
                    workers.remove(worker)
                    continue
                reason = (
                    "signal"
                    if stop_signal
                    else "batch_deadline"
                    if stopping
                    else "input_deadline"
                    if now - worker.started >= plan.per_input_seconds
                    else "orphaned_child"
                    if code is not None
                    else ""
                )
                if reason and not worker.stop_reason:
                    worker.stop_reason = reason
                    worker.term_at = now
                    if worker.process.pid in live_groups:
                        signal_group(worker.process.pid, signal.SIGTERM)
                elif (
                    worker.stop_reason
                    and now - worker.term_at >= 10
                    and worker.process.pid in live_groups
                ):
                    signal_group(worker.process.pid, signal.SIGKILL)
            time.sleep(0.2)
    finally:
        live_groups = groups()
        for worker in workers:
            if worker.process.pid in live_groups:
                signal_group(worker.process.pid, signal.SIGKILL)
            worker.process.wait()
            worker.log.close()
        remaining = set(owned) & groups()
        cleanup_deadline = time.monotonic() + 10
        while remaining and time.monotonic() < cleanup_deadline:
            time.sleep(0.1)
            remaining = set(owned) & groups()
        (args.output / "termination.json").write_text(
            json.dumps(
                {
                    "owned_process_groups": owned,
                    "remaining_live_groups": sorted(remaining),
                    "stop_signal": stop_signal,
                },
                indent=2,
            )
            + "\n"
        )
        assert not remaining

attempts = [
    json.loads(line)
    for line in (args.output / "attempts.jsonl").read_text().splitlines()
]
completed = [row["index"] for row in attempts if row["exit_code"] == 0]
missing = sorted(set(plan.indices) - set(completed))
(args.output / "summary.json").write_text(
    json.dumps(
        {
            "completed_indices": completed,
            "missing_indices": missing,
            "complete": not missing,
        },
        indent=2,
    )
    + "\n"
)
sys.exit(124 if missing else 0)
