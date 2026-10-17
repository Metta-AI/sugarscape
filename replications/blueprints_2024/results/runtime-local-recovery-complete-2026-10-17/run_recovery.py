"""Run declared runtime intervals and seal periodic completed-output checkpoints."""

import argparse
import hashlib
import io
import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import sys
import tarfile
import time
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class Group(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    model: Literal["altruisticHalfLookaheadBinary", "rawSugarscape"]
    steps: Literal[5000, 50000]
    start: int = Field(ge=0, lt=100)
    stop: int = Field(gt=0, le=100)


class Plan(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    groups: list[Group] = Field(min_length=1, max_length=2)
    seconds_per_group: int = Field(gt=0, le=21600)
    checkpoint_seconds: int = Field(gt=0, le=1800)


def checkpoint(root, names, ordinal):
    """Seal only ledger-committed outputs, leaving active native files untouched."""
    assert shutil.disk_usage(root).free >= 4 * 1024**3
    target = root / f"checkpoint-{ordinal:04d}.tar.gz"
    assert not target.exists()
    counts = {}
    with tarfile.open(target, "w:gz", compresslevel=1) as archive:
        archive.add(root / "plan.json", arcname="plan.json")
        archive.add(root / "run_recovery.py", arcname="run_recovery.py")
        for name in names:
            folder = root / name
            ledger_path = folder / "completed.jsonl"
            if not ledger_path.exists():
                continue
            ledger = ledger_path.read_bytes()
            if not ledger:
                continue
            assert ledger.endswith(b"\n")
            rows = [json.loads(line) for line in ledger.splitlines()]
            counts[name] = len(rows)
            for filename in ["manifest.json", "run_runtime.py", "source-sha256.json"]:
                archive.add(folder / filename, arcname=f"{name}/{filename}")
            info = tarfile.TarInfo(f"{name}/completed.jsonl")
            info.size = len(ledger)
            archive.addfile(info, io.BytesIO(ledger))
            for row in rows:
                assert row["exit_code"] == 0
                run = folder / row["entry"].removesuffix(".config")
                for filename, digest in row["files_sha256"].items():
                    path = run / filename
                    assert hashlib.sha256(path.read_bytes()).hexdigest() == digest
                    archive.add(path, arcname=f"{name}/{run.name}/{filename}")
    with target.open("rb") as stream:
        digest = hashlib.file_digest(stream, "sha256").hexdigest()
    receipt = {
        "archive": str(target),
        "bytes": target.stat().st_size,
        "sha256": digest,
        "counts": counts,
    }
    target.with_suffix(".receipt.json").write_text(json.dumps(receipt) + "\n")
    print("SNAPSHOT " + json.dumps(receipt), flush=True)


parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("source", type=Path)
parser.add_argument("plan", type=Path)
parser.add_argument("output", type=Path)
args = parser.parse_args()
source = args.source.resolve()
plan = Plan.model_validate_json(args.plan.read_bytes())
assert all(group.start < group.stop for group in plan.groups)
names = [f"{group.model}-{group.steps}" for group in plan.groups]
assert len(set(names)) == len(names)
assert hashlib.sha256((source / "run_runtime.py").read_bytes()).hexdigest() == (
    "df86e98f480c68abae4a3a647bcfe53bbce287c16850802e11c38eef8e6dd8d2"
)
root = args.output.resolve()
root.mkdir(parents=True, exist_ok=False)
(root / "plan.json").write_bytes(args.plan.read_bytes())
(root / "run_recovery.py").write_bytes(Path(__file__).read_bytes())
processes = []
signal.signal(signal.SIGTERM, lambda signum, frame: sys.exit(128 + signum))
try:
    for group, name in zip(plan.groups, names):
        command = [
            str(source / "venv/bin/python"),
            str(source / "run_runtime.py"),
            str(source / "engine"),
            str(source / "blueprints-runtimes.zip"),
            group.model,
            str(group.steps),
            str(root / name),
            "--start",
            str(group.start),
            "--stop",
            str(group.stop),
            "--seconds",
            str(plan.seconds_per_group),
        ]
        (root / f"{name}.command.json").write_text(json.dumps(command) + "\n")
        with (root / f"{name}.log").open("x") as log:
            processes.append(
                subprocess.Popen(
                    command,
                    stdout=log,
                    stderr=subprocess.STDOUT,
                    start_new_session=True,
                )
            )
    ordinal = 0
    deadline = time.monotonic() + plan.checkpoint_seconds
    while any(process.poll() is None for process in processes):
        if time.monotonic() >= deadline:
            ordinal += 1
            checkpoint(root, names, ordinal)
            deadline = time.monotonic() + plan.checkpoint_seconds
        time.sleep(1)
    statuses = [process.wait() for process in processes]
    (root / "terminal.json").write_text(json.dumps({"exit_codes": statuses}) + "\n")
    checkpoint(root, names, ordinal + 1)
finally:
    for process in processes:
        if process.poll() is None:
            os.killpg(process.pid, signal.SIGTERM)
            process.wait()
sys.exit(int(any(statuses)))
