"""Execute the frozen predictive evaluation after both full arms pass their audits."""

import hashlib
import json
import os
from pathlib import Path
import subprocess
import time

root = Path(__file__).resolve().parent
plan = json.loads((root / "analysis-plan.json").read_bytes())
for name, digest in plan["source_sha256"].items():
    assert hashlib.sha256((root / name).read_bytes()).hexdigest() == digest
assert not (root / "predictive").exists()
supervisor = json.loads((root / "process.json").read_bytes())["pid"]
deadline = time.monotonic() + 174000
while True:
    process = subprocess.run(
        ["ps", "-p", str(supervisor), "-o", "pid="],
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert process.returncode in [0, 1]
    if process.returncode == 1:
        break
    assert time.monotonic() < deadline
    time.sleep(60)
terminal = json.loads((root / "optimization-terminal.json").read_bytes())
assert terminal["exit_code"] == 0 and terminal["audited_epochs_per_method"] == 5000
for method in ["pathwise", "vargrad"]:
    assert json.loads((root / f"{method}-exit.json").read_bytes())["exit_code"] == 0
    assert json.loads((root / f"{method}-audit.json").read_bytes())["epochs"] == 5000
for name, digest in plan["source_sha256"].items():
    assert hashlib.sha256((root / name).read_bytes()).hexdigest() == digest
tools = root.parent.parent / "sugarscape-replication-tools"
runtime = root.parent / "quera-calibration-runtime-001"
env = dict(os.environ)
env.update(
    PYCALL_JL_RUNTIME_PYTHON=str(tools / "quera-flow-python-001/bin/python"),
    PYTHON=str(tools / "quera-flow-python-001/bin/python"),
    JULIA_DEPOT_PATH=":".join(
        str(path)
        for path in [
            runtime / "depot",
            tools / "julia-depot-1.11.3-001",
            tools / "julia-flow-depot-001",
        ]
    ),
    JULIA_NUM_THREADS="1",
    JULIA_NUM_PRECOMPILE_TASKS="2",
    JULIA_PKG_PRECOMPILE_AUTO="0",
    OPENBLAS_NUM_THREADS="1",
    R_LIBS_USER=str(tools / "R-library"),
)
command = [
    "/opt/homebrew/bin/gtimeout",
    "--signal=TERM",
    "--kill-after=30",
    "7200",
    str(tools / "julia-1.11.3-runtime-001/julia-1.11.3/bin/julia"),
    "--startup-file=no",
    "--project=" + str(runtime / "environment"),
    str(root / "predict.jl"),
]
with (root / "predictive-native.log").open("x") as stream:
    native = subprocess.run(
        command, env=env, stdout=stream, stderr=subprocess.STDOUT, timeout=7260
    )
(root / "predictive-native-exit.json").write_text(
    json.dumps({"exit_code": native.returncode, "command": command}, indent=2) + "\n"
)
assert native.returncode == 0
with (root / "predictive-audit.log").open("x") as stream:
    subprocess.run(
        [
            str(tools / "pdf-analysis-001/bin/python"),
            str(root / "analyze_predictive.py"),
            str(root),
            str(root / "predictive-summary.json"),
        ],
        stdout=stream,
        stderr=subprocess.STDOUT,
        timeout=1800,
        check=True,
    )
with (root / "predictive-r.log").open("x") as stream:
    subprocess.run(
        [
            "/opt/homebrew/bin/Rscript",
            "--vanilla",
            str(root / "verify_predictive.R"),
            str(root / "predictive"),
            str(root / "predictive-summary.json"),
            str(root / "predictive-r.json"),
        ],
        env=env,
        stdout=stream,
        stderr=subprocess.STDOUT,
        timeout=600,
        check=True,
    )
(root / "predictive-terminal.json").write_text(
    json.dumps(
        {
            "exit_code": 0,
            "native_trajectories": 4000,
            "python_audit_passed": True,
            "independent_r_arithmetic_passed": True,
            "publication_review_complete": False,
        },
        indent=2,
    )
    + "\n"
)
print("FULL_PREDICTIVE_EVALUATION_AUDITED", flush=True)
