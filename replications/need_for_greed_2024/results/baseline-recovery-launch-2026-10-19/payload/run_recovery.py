"""Recover frozen original inputs and compare every full trajectory with retained hashes."""

from concurrent.futures import FIRST_COMPLETED, ThreadPoolExecutor, wait
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tarfile
import time
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class Input(BaseModel):
    model_config = ConfigDict(extra="forbid")
    entry: str
    model: str
    seed: int
    configuration_sha256: str
    trajectory_sha256: str
    observations: int = Field(ge=1, le=5001)
    final_population: int = Field(ge=0, le=2500)


class Plan(BaseModel):
    model_config = ConfigDict(extra="forbid")
    workers: Literal[8]
    per_input_seconds: Literal[1800]
    admission_seconds: Literal[18000]
    rows: list[Input]


root = Path(__file__).resolve().parent
plan = Plan.model_validate_json((root / "plan.json").read_bytes())
assert len(plan.rows) == len({row.entry for row in plan.rows}) == 333
assert float(os.environ["GMN_CPU_LIMIT"]) >= plan.workers
assert sys.version.startswith("3.11.14")
(root / "runs").mkdir()
(root / "logs").mkdir()
started = time.monotonic()


def execute(row):
    target = root / "runs" / row.entry.removesuffix(".config")
    command = [
        "/usr/bin/timeout",
        "--kill-after=15s",
        "1840s",
        sys.executable,
        str(root / "run_native.py"),
        str(root / "engine"),
        str(root / "need-for-greed.zip"),
        row.entry,
        str(target),
        "--seconds",
        str(plan.per_input_seconds),
    ]
    with (root / "logs" / (row.entry + ".log")).open("x") as log:
        process = subprocess.run(command, stdout=log, stderr=subprocess.STDOUT)
    receipt = {"entry": row.entry, "exit_code": process.returncode, "command": command}
    if process.returncode == 0:
        result = json.loads((target / "result.json").read_bytes())
        raw = (target / "trajectory.json").read_bytes()
        receipt["prior_hash_exact"] = (
            hashlib.sha256(raw).hexdigest()
            == row.trajectory_sha256
            == result["trajectory_sha256"]
        )
        receipt["prior_counts_exact"] = (
            result["observations"] == row.observations
            and result["final_population"] == row.final_population
        )
        receipt["configuration_exact"] = (
            hashlib.sha256((target / "original.config").read_bytes()).hexdigest()
            == row.configuration_sha256
        )
        receipt["verified"] = all(
            receipt[key]
            for key in ("prior_hash_exact", "prior_counts_exact", "configuration_exact")
        )
    else:
        receipt["verified"] = False
    (root / "logs" / (row.entry + ".receipt.json")).write_text(
        json.dumps(receipt, indent=2) + "\n"
    )
    return receipt


def seal(number, records):
    archive = root / f"checkpoint-{number:04d}.tar.gz"
    with tarfile.open(archive, "x:gz") as tar:
        for name in (
            "plan.json",
            "run_native.py",
            "source-sha256.json",
            "run_recovery.py",
            "bootstrap.sh",
        ):
            tar.add(root / name, arcname=name)
        for record in records:
            entry = record["entry"]
            for directory in (root / "runs").iterdir():
                if directory.name == entry.removesuffix(".config"):
                    tar.add(directory, arcname="runs/" + directory.name)
            for suffix in (".log", ".receipt.json"):
                tar.add(
                    root / "logs" / (entry + suffix), arcname="logs/" + entry + suffix
                )
    print(
        "SNAPSHOT "
        + json.dumps(
            {
                "archive": str(archive),
                "bytes": archive.stat().st_size,
                "sha256": hashlib.sha256(archive.read_bytes()).hexdigest(),
            }
        ),
        flush=True,
    )


pending = iter(plan.rows)
records = []
delta = []
number = 0
stopping = False
with ThreadPoolExecutor(max_workers=plan.workers) as pool:
    active = {}
    while active or not stopping:
        while not stopping and len(active) < plan.workers:
            if time.monotonic() - started >= plan.admission_seconds:
                stopping = True
                break
            row = next(pending, None)
            if row is None:
                stopping = True
                break
            active[pool.submit(execute, row)] = row.entry
        if not active:
            break
        finished, _ = wait(active, return_when=FIRST_COMPLETED)
        for future in finished:
            record = future.result()
            del active[future]
            records.append(record)
            delta.append(record)
            print(json.dumps(record), flush=True)
            if not record["verified"]:
                stopping = True
        if len(delta) >= 25:
            number += 1
            seal(number, delta)
            delta = []
if delta:
    seal(number + 1, delta)
completed = {record["entry"] for record in records if record["verified"]}
summary = {
    "records": records,
    "verified_inputs": len(completed),
    "remaining": [row.entry for row in plan.rows if row.entry not in completed],
    "elapsed_seconds": time.monotonic() - started,
}
(root / "terminal.json").write_text(json.dumps(summary, indent=2) + "\n")
raise SystemExit(0 if len(completed) == len(plan.rows) else 1)
