"""Run a frozen supplementary cohort after full native CPython/PyPy pilot gates."""

import argparse
from concurrent.futures import FIRST_COMPLETED, ThreadPoolExecutor, wait
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tarfile
import time

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("root", type=Path)
args = parser.parse_args()
root = args.root.resolve()
plan = json.loads((root / "protocol.json").read_text())
assert plan["workers"] == 8 and plan["global_simulation_seconds"] == 34200
assert float(os.environ["GMN_CPU_LIMIT"]) >= 8
assert int(os.environ["GMN_MEMORY_LIMIT_BYTES"]) >= 8 * 1024**3
for folder in ["runs", "audits", "logs"]:
    (root / folder).mkdir(exist_ok=False)
interpreters = {
    "cpython": root / "cpython/bin/python",
    "pypy": root / "pypy/pypy3.11-v7.3.20-linux64/bin/pypy3",
}
versions = {
    kind: subprocess.check_output(
        [str(path), "-c", "import sys; print(sys.version)"], text=True
    ).strip()
    for kind, path in interpreters.items()
}
assert versions["cpython"].startswith("3.11.14")
assert versions["pypy"].startswith("3.11.13") and "PyPy 7.3.20" in versions["pypy"]
(root / "versions.json").write_text(json.dumps(versions, indent=2) + "\n")
started = time.monotonic()
completed = []
pilots = []
sealed = 0


def execute(row, runtime):
    """Run and independently audit one original input under a bounded interpreter."""
    remaining = min(
        plan["per_run_seconds"],
        int(plan["global_simulation_seconds"] - (time.monotonic() - started)),
    )
    if remaining <= 0:
        return {"status": "unstarted_budget", "entry": row["entry"], "runtime": runtime}
    original = (root / "inputs" / row["entry"]).read_bytes()
    assert hashlib.sha256(original).hexdigest() == row["configuration_sha256"]
    name = row["entry"].removesuffix(".config") + "-" + runtime
    target = root / "runs" / name
    audit = root / "audits" / name
    command = [
        "/usr/bin/timeout",
        "--signal=TERM",
        "--kill-after=15",
        str(remaining),
        sys.executable,
        str(root / "run_supplement.py"),
        str(root / "engine"),
        str(root / "blueprints-selfishness.zip"),
        "selfishness",
        row["entry"],
        str(target),
        "--interpreter",
        str(interpreters[runtime]),
    ]
    with (root / "logs" / (name + ".log")).open("x") as log:
        result = subprocess.run(command, stdout=log, stderr=subprocess.STDOUT)
        (root / "logs" / (name + ".exit.json")).write_text(
            json.dumps({"exit_code": result.returncode, "command": command}, indent=2)
            + "\n"
        )
        assert result.returncode == 0, (row["entry"], runtime, result.returncode)
        subprocess.run(
            [
                sys.executable,
                str(root / "audit_supplement.py"),
                str(root / "blueprints-selfishness.zip"),
                str(target),
                str(audit),
                "--expected-runtime",
                runtime,
            ],
            stdout=log,
            stderr=subprocess.STDOUT,
            timeout=120,
            check=True,
        )
    record = json.loads((target / "result.json").read_text())
    assert record["final_timestep"] == 5000 or record["final_population"] == 0
    assert record["observations"] == record["final_timestep"] + 1
    return {
        "status": "complete",
        "entry": row["entry"],
        "runtime": runtime,
        "directory": name,
        "trajectory_sha256": record["trajectory_sha256"],
        "observations": record["observations"],
        "elapsed_seconds": record["elapsed_seconds"],
    }


def seal(filename, records, include_pilots):
    """Seal only completed immutable runs, preserving a bounded export receipt."""
    output = root / filename
    with tarfile.open(output, "x:gz") as tar:
        for name in [
            "protocol.json",
            "versions.json",
            "run_supplement_batch.py",
            "run_supplement.py",
            "audit_supplement.py",
            "source-sha256.json",
            "bootstrap.sh",
        ]:
            tar.add(root / name, arcname=name, recursive=False)
        selected = records + (pilots if include_pilots else [])
        for record in selected:
            for directory in ["runs", "audits"]:
                tar.add(
                    root / directory / record["directory"],
                    arcname=directory + "/" + record["directory"],
                )
            for suffix in [".log", ".exit.json"]:
                name = record["directory"] + suffix
                tar.add(root / "logs" / name, arcname="logs/" + name, recursive=False)
        tar.add(root / "completed.jsonl", arcname="completed.jsonl", recursive=False)
        for status in ["pilot-gate.json", "complete.json"]:
            if (root / status).exists():
                tar.add(root / status, arcname=status, recursive=False)
        if filename == "terminal-evidence.tar.gz":
            successful = {record["directory"] for record in completed + pilots}
            # Retain failures and interrupted outputs separately from successful records.
            for path in sorted((root / "runs").iterdir()):
                if path.name not in successful:
                    tar.add(path, arcname="incomplete/runs/" + path.name)
            tar.add(root / "logs", arcname="all-logs")
    print(
        "SNAPSHOT "
        + json.dumps(
            {
                "archive": str(output),
                "bytes": output.stat().st_size,
                "sha256": hashlib.sha256(output.read_bytes()).hexdigest(),
                "completed_inputs_total": len(completed),
                "inputs_in_archive": len(records),
            }
        ),
        flush=True,
    )


with (root / "completed.jsonl").open("x") as ledger:
    try:
        for entry in plan["pilot_entries"]:
            row = next(row for row in plan["inputs"] if row["entry"] == entry)
            reference = execute(row, "cpython")
            assert reference["status"] == "complete"
            pilots.append(reference)
            candidate = execute(row, "pypy")
            assert candidate["status"] == "complete"
            assert (
                root / "runs" / reference["directory"] / "trajectory.json"
            ).read_bytes() == (
                root / "runs" / candidate["directory"] / "trajectory.json"
            ).read_bytes()
            completed.append(candidate)
            ledger.write(json.dumps(candidate) + "\n")
            ledger.flush()
        (root / "pilot-gate.json").write_text(
            json.dumps(
                {
                    "byte_exact_pairs": 2,
                    "paired_observation_counts": [
                        row["observations"] for row in completed
                    ],
                    "entries": plan["pilot_entries"],
                },
                indent=2,
            )
            + "\n"
        )
        seal("checkpoint-pilots.tar.gz", completed, True)
        sealed = len(completed)
        remaining = iter(
            row for row in plan["inputs"] if row["entry"] not in plan["pilot_entries"]
        )
        pool = ThreadPoolExecutor(max_workers=8)
        pending = {
            pool.submit(execute, row, "pypy") for _, row in zip(range(8), remaining)
        }
        try:
            while pending:
                finished, pending = wait(pending, return_when=FIRST_COMPLETED)
                for future in finished:
                    record = future.result()
                    if record["status"] == "complete":
                        completed.append(record)
                        ledger.write(json.dumps(record) + "\n")
                        ledger.flush()
                        if len(completed) - sealed >= 25:
                            seal(
                                f"checkpoint-{len(completed):04d}.tar.gz",
                                completed[sealed:],
                                False,
                            )
                            sealed = len(completed)
                    # Each completion frees one slot; budget exhaustion stops further submission.
                    if time.monotonic() - started < plan["global_simulation_seconds"]:
                        for _, row in zip(range(1), remaining):
                            pending.add(pool.submit(execute, row, "pypy"))
        finally:
            pool.shutdown(wait=True, cancel_futures=True)
        assert len({row["entry"] for row in completed}) == len(completed)
        (root / "complete.json").write_text(
            json.dumps(
                {
                    "completed_inputs": len(completed),
                    "requested_inputs": len(plan["inputs"]),
                    "all_complete": len(completed) == len(plan["inputs"]),
                    "elapsed_seconds": time.monotonic() - started,
                },
                indent=2,
            )
            + "\n"
        )
    finally:
        ledger.flush()
        seal("terminal-evidence.tar.gz", completed[sealed:], sealed == 0)
