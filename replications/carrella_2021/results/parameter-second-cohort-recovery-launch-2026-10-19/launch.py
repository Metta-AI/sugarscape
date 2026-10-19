"""Recover only explicitly unfinished independent inputs; preserve the failed attempt."""

import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import time

out = Path(__file__).resolve().parent
plan = json.loads((out / "plan.json").read_text())
original = Path(plan["original_cohort"])
for name, digest in plan["input_sha256"].items():
    assert hashlib.sha256(Path(name).read_bytes()).hexdigest() == digest
processes = subprocess.check_output(["ps", "-axo", "command"], text=True)
assert str(original / "model.py") not in processes
(out / "independent").mkdir()
started = time.monotonic()
with (out / "completed.jsonl").open("x") as ledger:
    for seed in plan["remaining_independent_seeds"]:
        assert shutil.disk_usage(out).free > 2 * 1024**3
        remaining = plan["wall_limit_seconds"] - (time.monotonic() - started)
        assert remaining > 0
        command = [
            "/Users/relh/Code/workspace/sugarscape-replications/.venv/bin/python",
            str(original / "model.py"),
            str(original / "independent-parameters" / f"{seed}.json"),
            str(out / "independent" / f"row-{seed}.csv"),
        ]
        before = time.monotonic()
        with (out / f"seed-{seed}.log").open("x") as log:
            result = subprocess.run(
                command, stdout=log, stderr=subprocess.STDOUT, timeout=remaining
            )
        receipt = {
            "seed": seed,
            "command": command,
            "exit_code": result.returncode,
            "elapsed_seconds": time.monotonic() - before,
        }
        ledger.write(json.dumps(receipt) + "\n")
        ledger.flush()
        print(json.dumps({"seed": seed, "exit_code": result.returncode}), flush=True)
        assert result.returncode == 0
        assert (
            sum(p.stat().st_size for p in out.rglob("*") if p.is_file())
            < plan["maximum_outputs_bytes"]
        )
(out / "complete.json").write_text(
    json.dumps(
        {
            "independent_runs": 20,
            "exit_code": 0,
            "elapsed_seconds": time.monotonic() - started,
        }
    )
    + "\n"
)
