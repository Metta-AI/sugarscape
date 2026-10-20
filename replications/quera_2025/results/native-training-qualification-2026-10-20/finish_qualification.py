"""Finish the existing pathwise run, then qualify the separate VarGrad workflow."""

import csv
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import time

root = Path(__file__).resolve().parent
launch = json.loads((root / "launch.json").read_bytes())
for name, digest in launch["source_sha256"].items():
    assert hashlib.sha256((root / name).read_bytes()).hexdigest() == digest
deadline = time.monotonic() + 1900
while True:
    status = subprocess.run(
        ["ps", "-p", str(launch["native_pid"]), "-o", "pid="],
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert status.returncode in [0, 1]
    if status.returncode == 1:
        break
    assert time.monotonic() < deadline
    time.sleep(20)
assert (root / "pathwise-001/completion.txt").is_file()
python = "/Users/relh/Code/workspace/sugarscape-replication-tools/pdf-analysis-001/bin/python"
with (root / "pathwise-audit.log").open("x") as stream:
    result = subprocess.run(
        [
            python,
            str(root / "audit_training.py"),
            str(root / "pathwise-001"),
            str(root / "pathwise-audit.json"),
        ],
        stdout=stream,
        stderr=subprocess.STDOUT,
        timeout=120,
    )
assert result.returncode == 0
runtime = root.parent / "quera-calibration-runtime-001"
env = dict(os.environ)
tools = root.parent.parent / "sugarscape-replication-tools"
env.update(
    PYCALL_JL_RUNTIME_PYTHON=str(tools / "quera-flow-python-001/bin/python"),
    PYTHON=str(tools / "quera-flow-python-001/bin/python"),
    JULIA_DEPOT_PATH=":".join(
        map(
            str,
            [
                runtime / "depot",
                tools / "julia-depot-1.11.3-001",
                tools / "julia-flow-depot-001",
            ],
        )
    ),
    JULIA_NUM_THREADS="1",
    JULIA_NUM_PRECOMPILE_TASKS="2",
    JULIA_PKG_PRECOMPILE_AUTO="0",
    OPENBLAS_NUM_THREADS="1",
)
assert not (root / "vargrad-001").exists()
command = [
    "/opt/homebrew/bin/gtimeout",
    "--signal=TERM",
    "--kill-after=30",
    "1800",
    str(tools / "julia-1.11.3-runtime-001/julia-1.11.3/bin/julia"),
    "--startup-file=no",
    "--project=" + str(runtime / "environment"),
    str(root / "train.jl"),
    "VarGrad",
    str(root / "vargrad-001"),
    "3",
]
with (root / "vargrad-001.log").open("x") as stream:
    result = subprocess.run(
        command, env=env, stdout=stream, stderr=subprocess.STDOUT, timeout=1860
    )
(root / "vargrad-exit.json").write_text(
    json.dumps({"exit_code": result.returncode, "command": command}, indent=2) + "\n"
)
assert result.returncode == 0
with (root / "vargrad-audit.log").open("x") as stream:
    subprocess.run(
        [
            python,
            str(root / "audit_training.py"),
            str(root / "vargrad-001"),
            str(root / "vargrad-audit.json"),
        ],
        stdout=stream,
        stderr=subprocess.STDOUT,
        timeout=120,
        check=True,
    )
assert (root / "pathwise-001/initial-parameters.csv").read_bytes() == (
    root / "vargrad-001/initial-parameters.csv"
).read_bytes()
negative = root / "negative-optimizer-control"
shutil.copytree(root / "pathwise-001", negative)
parameter_file = negative / "parameters-1.csv"
rows = parameter_file.read_text().splitlines()
rows[0] = str(float(rows[0]) + 0.01)
parameter_file.write_text("\n".join(rows) + "\n")
with (root / "negative-optimizer.log").open("x") as stream:
    rejected = subprocess.run(
        [
            python,
            str(root / "audit_training.py"),
            str(negative),
            str(negative / "unexpected-pass.json"),
        ],
        stdout=stream,
        stderr=subprocess.STDOUT,
        timeout=120,
    )
assert rejected.returncode != 0 and not (negative / "unexpected-pass.json").exists()
timings = {}
for method in ["pathwise", "vargrad"]:
    with (root / f"{method}-001/epochs.csv").open() as stream:
        epochs = list(csv.DictReader(stream))
    timings[method] = {
        "first_epoch_including_compilation_seconds": float(epochs[0]["elapsed_seconds"]),
        "later_epoch_seconds": [
            float(right["elapsed_seconds"]) - float(left["elapsed_seconds"])
            for left, right in zip(epochs, epochs[1:])
        ],
    }
(root / "qualification.json").write_text(
    json.dumps(
        {
            "methods": ["pathwise", "VarGrad"],
            "epochs_each": 3,
            "native_workflows_audited": True,
            "initial_flows_byte_identical": True,
            "corrupted_optimizer_update_rejected": True,
            "timings": timings,
            "full_training_launched": False,
            "scope": "Complete native optimizer qualification, not full calibration or paper replication.",
        },
        indent=2,
    )
    + "\n"
)
print("BOTH_NATIVE_TRAINING_WORKFLOWS_QUALIFIED", flush=True)
