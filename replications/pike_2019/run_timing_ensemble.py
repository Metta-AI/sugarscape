"""Run serial native parity controls, then the declared 900-condition timing grid."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import random
import shutil
import subprocess
import sys
import time

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("engine", type=Path)
parser.add_argument("library", type=Path)
parser.add_argument("output", type=Path)
args = parser.parse_args()
assert platform.python_version() == "3.11.14"
root = args.output.resolve()
root.mkdir(parents=True, exist_ok=False)
source = Path(__file__).resolve().parent
for name in [
    "run.py",
    "run_timing.py",
    "run_groups.py",
    "run_timing_ensemble.py",
    "TIMING_PROTOCOL.md",
]:
    shutil.copy2(source / name, root / name)
for flavor, runner in [("observed", "run.py"), ("timed", "run_timing.py")]:
    stage = root / flavor
    stage.mkdir()
    shutil.copy2(root / runner, stage / "run.py")
    shutil.copy2(root / "run_groups.py", stage / "run_groups.py")
conditions = [(name, [name]) for name in ["standard", "explicit", "network"]]
conditions += [
    (f"{approach}-{policy}", [approach, "10", policy])
    for approach in ["explicit", "network"]
    for policy in ["none", "movement"]
]
conditions += [(name, [name]) for name in ["common-one", "common-multi"]]
schedule = []
scheduler = random.Random(20261017)
for seed in range(100):
    block = conditions.copy()
    scheduler.shuffle(block)
    schedule.extend(
        {"seed": seed, "condition": name, "arguments": arguments}
        for name, arguments in block
    )
environment = os.environ | {
    "PYTHONHASHSEED": "0",
    "PYTHONDONTWRITEBYTECODE": "1",
    "OPENBLAS_NUM_THREADS": "1",
    "OMP_NUM_THREADS": "1",
    "MKL_NUM_THREADS": "1",
}
manifest = {
    "required_runs": 900,
    "control_seed": 1001,
    "control_pairs": 9,
    "workers": 1,
    "schedule": schedule,
    "python": platform.python_version(),
    "platform": platform.platform(),
    "cpu_count": os.cpu_count(),
    "affinity": sorted(os.sched_getaffinity(0)),
    "thread_environment": {
        key: environment[key]
        for key in ["OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"]
    },
    "source_sha256": {
        p.name: hashlib.sha256(p.read_bytes()).hexdigest()
        for p in root.iterdir()
        if p.is_file()
    },
    "scope": "Dedicated node, serial paired blocks; controls excluded from timing estimates. Common-resource nonfinite states are not repaired.",
}
(root / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
started = time.monotonic()


def execute(flavor, name, arguments, seed, prefix):
    assert shutil.disk_usage(root).free >= 4 * 1024**3
    remaining = 43200 - (time.monotonic() - started)
    assert remaining > 0
    target = root / f"{prefix}-{flavor}-{name}-{seed}"
    script = root / flavor / ("run_groups.py" if len(arguments) == 3 else "run.py")
    command = [
        sys.executable,
        str(script),
        str(args.engine.resolve()),
        str(args.library.resolve()),
        *arguments,
        str(seed),
        str(target),
    ]
    with target.with_suffix(".log").open("x") as log:
        result = subprocess.run(
            command,
            stdout=log,
            stderr=subprocess.STDOUT,
            env=environment,
            timeout=min(300, remaining),
        )
    receipt = {
        "condition": name,
        "seed": seed,
        "flavor": flavor,
        "command": command,
        "exit_code": result.returncode,
    }
    target.with_suffix(".exit.json").write_text(json.dumps(receipt) + "\n")
    assert result.returncode == 0, receipt
    hashes = {}
    for path in sorted(target.rglob("*")):
        if path.is_file():
            with path.open("rb") as stream:
                hashes[str(path.relative_to(target))] = hashlib.file_digest(
                    stream, "sha256"
                ).hexdigest()
    receipt["sha256"] = hashes
    return receipt


controls = []
for name, arguments in conditions:
    observed = execute("observed", name, arguments, 1001, "control")
    timed = execute("timed", name, arguments, 1001, "control")
    prefix = "run/" if len(arguments) == 3 else ""
    files = [
        prefix + name
        for name in [
            "initial-agents.json",
            "prices.json",
            "population.csv",
            "health.csv",
        ]
    ]
    assert all(observed["sha256"][name] == timed["sha256"][name] for name in files)
    controls.append(
        {"condition": name, "exact_files": files, "observed": observed, "timed": timed}
    )
    (root / "parity-progress.json").write_text(json.dumps(controls, indent=2) + "\n")
(root / "parity-complete.json").write_text(
    json.dumps({"pairs": 9, "exact_files": 36, "controls": controls}, indent=2) + "\n"
)
with (root / "completed.jsonl").open("x") as ledger:
    for ordinal, item in enumerate(schedule):
        receipt = execute(
            "timed", item["condition"], item["arguments"], item["seed"], "ensemble"
        )
        receipt["ordinal"] = ordinal
        ledger.write(json.dumps(receipt) + "\n")
        ledger.flush()
(root / "complete.json").write_text(
    json.dumps(
        {
            "completed_runs": 900,
            "parity_pairs": 9,
            "elapsed_seconds": time.monotonic() - started,
        }
    )
    + "\n"
)
