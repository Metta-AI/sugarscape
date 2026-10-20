"""Run both full frozen calibration arms only after native qualification passes."""

import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import time

root = Path(__file__).resolve().parent
protocol = json.loads((root / "protocol.json").read_bytes())
campaign = protocol["full_campaign"]
qualification = json.loads(Path(campaign["requires_qualification"]).read_bytes())
assert qualification["native_workflows_audited"]
assert qualification["initial_flows_byte_identical"]
assert qualification["corrupted_optimizer_update_rejected"]
assert json.loads(Path(campaign["requires_native_pathwise_exit_zero"]).read_bytes())[
    "exit_code"
] == 0
for name, digest in campaign["source_sha256"].items():
    assert hashlib.sha256((root / name).read_bytes()).hexdigest() == digest
assert not (root / "admission.json").exists()
free = shutil.disk_usage(root).free
assert free > campaign["minimum_free_bytes"]
(root / "admission.json").write_text(
    json.dumps(
        {
            "unix": time.time(),
            "free_bytes": free,
            "protocol_sha256": hashlib.sha256(
                (root / "protocol.json").read_bytes()
            ).hexdigest(),
            "qualification_sha256": hashlib.sha256(
                Path(campaign["requires_qualification"]).read_bytes()
            ).hexdigest(),
            "cloud_reservation_usd": 0,
            "no_retry": True,
        },
        indent=2,
    )
    + "\n"
)
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
)
for method in campaign["methods"]:
    output = root / method.lower()
    assert not output.exists()
    command = [
        "/opt/homebrew/bin/gtimeout",
        "--signal=TERM",
        "--kill-after=30",
        str(campaign["maximum_seconds_per_method"]),
        str(tools / "julia-1.11.3-runtime-001/julia-1.11.3/bin/julia"),
        "--startup-file=no",
        "--project=" + str(runtime / "environment"),
        str(root / "train.jl"),
        method,
        str(output),
        str(campaign["epochs_per_method"]),
    ]
    started = time.time()
    with (root / f"{method.lower()}.log").open("x") as stream:
        native = subprocess.Popen(
            command, env=env, stdout=stream, stderr=subprocess.STDOUT
        )
        (root / f"{method.lower()}-launch.json").write_text(
            json.dumps(
                {"pid": native.pid, "started_unix": started, "command": command},
                indent=2,
            )
            + "\n"
        )
        exit_code = native.wait(timeout=campaign["maximum_seconds_per_method"] + 60)
    (root / f"{method.lower()}-exit.json").write_text(
        json.dumps(
            {"exit_code": exit_code, "elapsed_seconds": time.time() - started},
            indent=2,
        )
        + "\n"
    )
    assert exit_code == 0
    with (root / f"{method.lower()}-audit.log").open("x") as stream:
        subprocess.run(
            [
                str(tools / "pdf-analysis-001/bin/python"),
                str(root / "audit_training.py"),
                str(output),
                str(root / f"{method.lower()}-audit.json"),
            ],
            stdout=stream,
            stderr=subprocess.STDOUT,
            timeout=1800,
            check=True,
        )
assert (root / "pathwise/initial-parameters.csv").read_bytes() == (
    root / "vargrad/initial-parameters.csv"
).read_bytes()
(root / "optimization-terminal.json").write_text(
    json.dumps(
        {
            "exit_code": 0,
            "audited_epochs_per_method": 5000,
            "initial_flows_byte_identical": True,
            "posterior_analysis_complete": False,
        },
        indent=2,
    )
    + "\n"
)
print("BOTH_FULL_OPTIMIZATION_ARMS_AUDITED", flush=True)
