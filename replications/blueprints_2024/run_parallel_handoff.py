"""Run disjoint remaining Bentham inputs after a recorded local-producer handoff."""

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
import gzip
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time
from typing import Literal
import zipfile

from pydantic import BaseModel, ConfigDict, Field

from run import ARCHIVE_SHA256, Configuration


class StopReceipt(BaseModel):
    model_config = ConfigDict(extra="forbid")
    local_parent_pid: Literal[18256]
    stopped_at: datetime
    native_process_ids: list[int]
    terminal_process_ids: list[int]
    completed_ledger_sha256: str
    partial_attempt_preserved: bool


class Handoff(BaseModel):
    model_config = ConfigDict(extra="forbid")
    model: Literal["benthamHalfLookaheadBinary"]
    local_completed_start: Literal[20]
    completed_prefix_end: int = Field(ge=20, lt=500)
    remaining_indices: list[int]
    workers: Literal[32]
    per_input_limit_seconds: Literal[3600]
    stop_receipt_sha256: str
    qualification_trajectory_sha256: Literal[
        "d191dbe7daa4e1aafd807d727c1eee48288c08436c0104f822b79c0b985bbebb"
    ]


parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("engine", type=Path)
parser.add_argument("archive", type=Path)
parser.add_argument("qualification", type=Path)
parser.add_argument("plan", type=Path)
parser.add_argument("stop_receipt", type=Path)
parser.add_argument("local_completed_ledger", type=Path)
parser.add_argument("output", type=Path)
args = parser.parse_args()
assert sys.version_info[:3] == (3, 11, 14)
plan = Handoff.model_validate_json(args.plan.read_bytes())
stop_bytes = args.stop_receipt.read_bytes()
assert hashlib.sha256(stop_bytes).hexdigest() == plan.stop_receipt_sha256
stop = StopReceipt.model_validate_json(stop_bytes)
assert stop.stopped_at.utcoffset() is not None
assert stop.partial_attempt_preserved
assert len(set(stop.native_process_ids)) == len(stop.native_process_ids)
assert set(stop.terminal_process_ids) == {
    stop.local_parent_pid,
    *stop.native_process_ids,
}
ledger_bytes = args.local_completed_ledger.read_bytes()
assert hashlib.sha256(ledger_bytes).hexdigest() == stop.completed_ledger_sha256
prior = [json.loads(line) for line in ledger_bytes.splitlines()]
assert len(prior) + plan.local_completed_start == plan.completed_prefix_end
assert plan.remaining_indices == list(range(plan.completed_prefix_end, 500))
assert hashlib.sha256(args.archive.read_bytes()).hexdigest() == ARCHIVE_SHA256
with zipfile.ZipFile(args.archive) as archive:
    configs = [
        Configuration.model_validate_json(archive.read(n)) for n in archive.namelist()
    ]
seeds = sorted(c.seed for c in configs if c.agentDecisionModels == [plan.model])
assert len(seeds) == len(set(seeds)) == 500
assert [row["seed"] for row in prior] == seeds[20 : plan.completed_prefix_end]
assert (args.qualification / "exit-code.txt").read_text().strip() == "0"
qualified = [
    json.loads(line)
    for line in (args.qualification / "qualification/completed.jsonl")
    .read_text()
    .splitlines()
]
assert len(qualified) == 1 and qualified[0]["seed"] == seeds[20]
assert (
    qualified[0]["result"]["trajectory_sha256"] == plan.qualification_trajectory_sha256
)
trajectory = (
    args.qualification / "qualification" / f"seed-{seeds[20]}" / "trajectory.json.gz"
)
compressed = trajectory.read_bytes()
assert hashlib.sha256(compressed).hexdigest() == qualified[0]["compressed_sha256"]
raw = gzip.decompress(compressed)
assert hashlib.sha256(raw).hexdigest() == plan.qualification_trajectory_sha256
assert len(json.loads(raw)) == 5001
assets = Path(__file__).resolve().parent
qualified_manifest = json.loads(
    (args.qualification / "qualification/manifest.json").read_text()
)
for name, field in (
    ("run.py", "runner_sha256"),
    ("run_batch.py", "batch_runner_sha256"),
):
    assert (
        hashlib.sha256((assets / name).read_bytes()).hexdigest()
        == qualified_manifest[field]
    )
affinity = sorted(os.sched_getaffinity(0))
assert len(affinity) == 64
root = args.output.resolve()
root.mkdir(parents=True, exist_ok=False)
(root / "plan.json").write_bytes(args.plan.read_bytes())
(root / "stop-receipt.json").write_bytes(stop_bytes)
(root / "local-completed.jsonl").write_bytes(ledger_bytes)
(root / "start.json").write_text(
    json.dumps(
        {
            "unix": time.time(),
            "affinity": affinity,
            "runner_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            "python": sys.version,
        }
    )
    + "\n"
)


def run_input(index):
    command = [
        "timeout",
        "--signal=TERM",
        "--kill-after=30",
        str(plan.per_input_limit_seconds),
        sys.executable,
        str(assets / "run_batch.py"),
        str(args.engine.resolve()),
        str(args.archive.resolve()),
        plan.model,
        str(root / f"input-{index:03d}"),
        "--start",
        str(index),
        "--stop",
        str(index + 1),
    ]
    started = time.monotonic()
    with (root / f"input-{index:03d}.log").open("xb") as log:
        result = subprocess.run(command, stdout=log, stderr=subprocess.STDOUT)
    record = {
        "index": index,
        "seed": seeds[index],
        "command": command,
        "exit_code": result.returncode,
        "elapsed_seconds": time.monotonic() - started,
    }
    if result.returncode == 0:
        rows = [
            json.loads(line)
            for line in (root / f"input-{index:03d}/completed.jsonl")
            .read_text()
            .splitlines()
        ]
        assert len(rows) == 1 and rows[0]["seed"] == seeds[index]
        record["completed_ledger_sha256"] = hashlib.sha256(
            (root / f"input-{index:03d}/completed.jsonl").read_bytes()
        ).hexdigest()
    return record


records = []
with (root / "attempts.jsonl").open("x") as ledger:
    with ThreadPoolExecutor(max_workers=plan.workers) as pool:
        futures = [pool.submit(run_input, index) for index in plan.remaining_indices]
        for future in as_completed(futures):
            record = future.result()
            ledger.write(json.dumps(record) + "\n")
            ledger.flush()
            records.append(record)
            print(json.dumps(record), flush=True)
report = {
    "requested_inputs": len(plan.remaining_indices),
    "completed_inputs": sum(row["exit_code"] == 0 for row in records),
    "failed_indices": sorted(row["index"] for row in records if row["exit_code"] != 0),
    "scope": "Execution receipt only. Every trajectory requires independent audit and union reconciliation before coverage credit.",
}
(root / "terminal.json").write_text(json.dumps(report, indent=2) + "\n")
assert report["completed_inputs"] == report["requested_inputs"], report
