"""Prepare one frozen, unassigned sweep shard; never allocate or launch compute."""

import argparse
import gzip
import hashlib
import json
from pathlib import Path
import shutil
from typing import Literal
import zipfile

from pydantic import BaseModel, ConfigDict, TypeAdapter


class Input(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    experiment: Literal["selfishness"]
    condition: str
    seed: str
    entry: str
    configuration_sha256: str


parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("paper_archive", type=Path)
parser.add_argument("blueprints_archive", type=Path)
parser.add_argument("inventory", type=Path)
parser.add_argument("output", type=Path)
parser.add_argument("--batch", type=int, choices=range(19), required=True)
args = parser.parse_args()
source = Path(__file__).resolve().parent
study = source.parent
prepared = study / "results/unassigned-sweep-preparation-2026-10-19/prepared"
plan = json.loads((prepared / "plan.json").read_bytes())
assert plan["inputs"] == 9597 and plan["batches"] == 19
assert plan["batch_admission_seconds"] == 41400 and plan["batch_outer_seconds"] == 42800
shard = prepared / f"batch-{args.batch:02d}.json.gz"
assert (
    hashlib.sha256(shard.read_bytes()).hexdigest() == plan["shards_sha256"][shard.name]
)
rows = TypeAdapter(list[Input]).validate_json(gzip.decompress(shard.read_bytes()))
entries = {row.entry for row in rows}
assert len(entries) == len(rows) == plan["batch_sizes"][args.batch]
inventory = json.loads(args.inventory.read_bytes())
completed = {row["entry"] for row in inventory["runs"]}
assert len(completed) == len(inventory["runs"]) == inventory["audited_inputs"]
assert entries.isdisjoint(completed), (
    "Shard overlaps audited work; reconcile before preparation"
)
prior = study / "results/table4-missing-conditions-2026-10-19/recovery"
reference = json.loads((prior / "protocol.json").read_bytes())
assert entries.isdisjoint(row["entry"] for row in reference["inputs"])
assert (
    hashlib.sha256(args.paper_archive.read_bytes()).hexdigest()
    == reference["need_for_greed_archive_sha256"]
)
assert (
    hashlib.sha256(args.blueprints_archive.read_bytes()).hexdigest()
    == reference["original_archive_sha256"]
)
assert not args.output.exists()
args.output.mkdir(parents=True)
(args.output / "inputs").mkdir()
with (
    zipfile.ZipFile(args.paper_archive) as paper,
    zipfile.ZipFile(args.blueprints_archive) as blueprints,
):
    for row in rows:
        raw = paper.read(row.entry)
        assert raw == blueprints.read(row.entry)
        assert hashlib.sha256(raw).hexdigest() == row.configuration_sha256
        config = json.loads(raw)
        assert str(config["seed"]) == row.seed and config["timesteps"] == 5000
        assert Path(row.entry).name == row.entry and row.entry.endswith(".config")
        (args.output / "inputs" / row.entry).write_bytes(raw)
for name in ["run_supplement.py", "audit_supplement.py", "source-sha256.json"]:
    shutil.copyfile(prior / name, args.output / name)
for name in ["run_supplement_batch.py", "bootstrap.sh"]:
    shutil.copyfile(source / name, args.output / name)
protocol = {
    key: reference[key]
    for key in [
        "experiment",
        "source_revision",
        "source_sha256",
        "runtime_url",
        "runtime_sha256",
        "original_archive_sha256",
        "need_for_greed_archive_sha256",
        "remaining_worklist_sha256",
        "native_steps",
        "observations",
        "completion_rule",
        "checkpoint_every_completed_inputs",
    ]
}
protocol.update(
    inputs=[row.model_dump() for row in rows],
    pilot_entries=[rows[0].entry, rows[-1].entry],
    pilot_gate="First and last frozen shard entries must match full CPython/PyPy trajectories before parallel admission; count each original input once.",
    workers=8,
    global_simulation_seconds=41400,
    per_run_seconds=1800,
    outer_seconds=42800,
    outer_kill_grace_seconds=30,
    admission_clock="Linux CLOCK_BOOTTIME; captured before setup by bootstrap.sh",
    run_admission_reserve_seconds=135,
    batch_index=args.batch,
    conditions=sorted({row.condition for row in rows}, key=float),
    scope="Prepared frozen shard only. Budget approval, current price and assignment checks, and a globally reserved attempt budget are required before launch. No automatic retries.",
)
(args.output / "protocol.json").write_text(json.dumps(protocol, indent=2) + "\n")
files = {
    str(p.relative_to(args.output)): hashlib.sha256(p.read_bytes()).hexdigest()
    for p in sorted(args.output.rglob("*"))
    if p.is_file()
}
report = {
    "batch": args.batch,
    "inputs": len(rows),
    "frozen_plan_sha256": hashlib.sha256(
        (prepared / "plan.json").read_bytes()
    ).hexdigest(),
    "shard_sha256": hashlib.sha256(shard.read_bytes()).hexdigest(),
    "inventory_sha256": hashlib.sha256(args.inventory.read_bytes()).hexdigest(),
    "file_sha256": files,
    "scope": "Original-input and payload preparation only; no runtime qualification, allocation, or simulation.",
}
(args.output / "preparation.json").write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps({key: value for key, value in report.items() if key != "file_sha256"}))
