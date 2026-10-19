"""Reconcile confirmed successful runs while retaining the original cohort timeout."""

import hashlib
import json
from pathlib import Path
import shutil
import subprocess

base = Path(__file__).resolve().parent
original = base / "row-1525"
recovery = base / "row-1525-recovery-001"
out = base / "row-1525-reconciled-001"
assert not out.exists()
plan_bytes = (recovery / "plan.json").read_bytes()
plan = json.loads(plan_bytes)
finished = json.loads((recovery / "complete.json").read_text())
assert finished["independent_runs"] == 10 and finished["exit_code"] == 0
assert finished["elapsed_seconds"] <= plan["wall_limit_seconds"]
assert (
    hashlib.sha256((original / "protocol.json").read_bytes()).hexdigest()
    == plan["original_protocol_sha256"]
)
for name, digest in plan["input_sha256"].items():
    assert hashlib.sha256(Path(name).read_bytes()).hexdigest() == digest
cohorts = [
    json.loads(line) for line in (base / "cohorts.jsonl").read_text().splitlines()
]
assert next(row for row in cohorts if row["original_row"] == 1525)["exit_code"] == 1
old = [
    json.loads(line) for line in (original / "completed.jsonl").read_text().splitlines()
]
new = [
    json.loads(line) for line in (recovery / "completed.jsonl").read_text().splitlines()
]
assert [r["name"] for r in old] == ["native"] + [f"independent-{s}" for s in range(54)]
assert [r["seed"] for r in new] == list(range(54, 64))
assert all(r["exit_code"] == 0 for r in old + new)
assert plan["remaining_independent_seeds"] == list(range(54, 64))
commands = dict(json.loads((original / "commands.json").read_text()))
assert commands["native"][-3:] == ["0", "64", str(original / "native")]
for receipt in new:
    expected = commands[f"independent-{receipt['seed']}"][:]
    expected[-1] = str(recovery / "independent" / f"row-{receipt['seed']}.csv")
    assert receipt["command"] == expected
assert not (original / "complete.json").exists()
processes = subprocess.check_output(["ps", "-axo", "command"], text=True)
assert str(recovery / "launch.py") not in processes
out.mkdir()
for name in [
    "protocol.json",
    "parameters.csv",
    "model.py",
    "Replay.java",
    "Replay.class",
    "commands.json",
]:
    shutil.copyfile(original / name, out / name)
shutil.copytree(original / "independent-parameters", out / "independent-parameters")
for engine in ["native", "independent"]:
    (out / engine).mkdir()
provenance = {}
for engine in ["native", "independent"]:
    for seed in range(64):
        source = recovery if engine == "independent" and seed >= 54 else original
        name = f"{engine}/row-{seed}.csv"
        raw = (source / name).read_bytes()
        (out / name).write_bytes(raw)
        provenance[name] = {
            "source": str(source / name),
            "sha256": hashlib.sha256(raw).hexdigest(),
        }
combined = old + [
    {
        "name": f"independent-{r['seed']}",
        "exit_code": r["exit_code"],
        "elapsed_seconds": r["elapsed_seconds"],
    }
    for r in new
]
(out / "completed.jsonl").write_text(
    "".join(json.dumps(row) + "\n" for row in combined)
)
(out / "complete.json").write_text(
    json.dumps({"native_runs": 64, "independent_runs": 64, "exit_code": 0}) + "\n"
)
record = {
    "scope": "Derived completion manifest: every constituent simulation has a verified zero exit receipt. This is not the original cohort launcher exit status, which remains1. Original failure, interrupted seed54 and recovery receipts are retained. No successful input is rerun or counted twice.",
    "original_terminal": next(row for row in cohorts if row["original_row"] == 1525),
    "original_receipts": old,
    "recovery_receipts": new,
    "recovery_complete": finished,
    "recovery_plan_sha256": hashlib.sha256(plan_bytes).hexdigest(),
    "interrupted_seed54_sha256": hashlib.sha256(
        (original / "independent/row-54.csv").read_bytes()
    ).hexdigest(),
    "trajectories": provenance,
}
(out / "reconciliation.json").write_text(json.dumps(record, indent=2) + "\n")
root = base.parent.parent
repo = root / "sugarscape-carrella/replications/carrella_2021"
subprocess.run(
    [
        str(root / "sugarscape-replications/.venv/bin/python"),
        str(repo / "audit_seed_ensemble.py"),
        str(out),
        str(out / "audit"),
    ],
    check=True,
)
subprocess.run(
    [
        str(root / "sugarscape-replication-tools/pdf-analysis-001/bin/python"),
        str(repo / "compare_seed_cohorts.py"),
        str(out / "protocol.json"),
        str(out / "audit/runs.csv"),
        str(out / "comparison"),
    ],
    check=True,
    stdout=(base / "row-1525-reconciled-comparison.log").open("w"),
)
print("Reconciled and audited128 successful runs; original timeout retained.")
