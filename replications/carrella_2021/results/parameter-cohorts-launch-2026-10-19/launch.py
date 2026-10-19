"""Run the frozen outcome-blind parameter cohorts sequentially, preserving failures."""

import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import time

out = Path(__file__).resolve().parent
root = out.parent.parent
python = root / "sugarscape-replications/.venv/bin/python"
numpy_python = root / "sugarscape-replication-tools/pdf-analysis-001/bin/python"
repo = root / "sugarscape-carrella/replications/carrella_2021"
plan = json.loads((out / "plan.json").read_text())
for path, digest in json.loads((out / "frozen-sha256.json").read_text()).items():
    assert hashlib.sha256(Path(path).read_bytes()).hexdigest() == digest
started = time.monotonic()
with (out / "cohorts.jsonl").open("x") as ledger:
    for index in plan["original_rows_zero_based"]:
        assert time.monotonic() - started < 7200
        assert shutil.disk_usage(out).free > plan["minimum_free_bytes"]
        assert (
            sum(p.stat().st_size for p in out.rglob("*") if p.is_file())
            < plan["maximum_outputs_bytes"]
        )
        cohort = out / f"row-{index}"
        with (cohort / "launcher.log").open("x") as log:
            result = subprocess.run(
                [str(python), str(cohort / "launch.py")],
                stdout=log,
                stderr=subprocess.STDOUT,
            )
        receipt = {
            "original_row": index,
            "exit_code": result.returncode,
            "elapsed_total_seconds": time.monotonic() - started,
        }
        ledger.write(json.dumps(receipt) + "\n")
        ledger.flush()
        print(json.dumps(receipt), flush=True)
        if result.returncode != 0:
            continue
        subprocess.run(
            [
                str(python),
                str(repo / "audit_seed_ensemble.py"),
                str(cohort),
                str(cohort / "audit"),
            ],
            check=True,
            timeout=60,
        )
        subprocess.run(
            [
                str(numpy_python),
                str(repo / "compare_seed_cohorts.py"),
                str(cohort / "protocol.json"),
                str(cohort / "audit/runs.csv"),
                str(cohort / "comparison.json"),
            ],
            check=True,
            timeout=60,
        )
(out / "dispatch-complete.json").write_text(
    json.dumps(
        {
            "cohorts_attempted": 10,
            "elapsed_seconds": time.monotonic() - started,
            "scope": "Dispatch completion only; inspect all exit codes and audits.",
        }
    )
    + "\n"
)
