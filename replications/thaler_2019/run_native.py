"""Run four complete original 1000-step Sugarscape workflows; no timing verdict."""

import argparse
import hashlib
import json
import os
import platform
import subprocess
import time
from pathlib import Path

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("source", type=Path)
parser.add_argument("fidelity", type=Path)
parser.add_argument("output", type=Path)
args = parser.parse_args()
source = args.source.resolve()
output = args.output.resolve()
assert platform.system() == "Linux"
fidelity = json.loads(args.fidelity.read_text())
pins = fidelity["hashes"]["timing"]
for name, expected in pins.items():
    assert hashlib.sha256((source / name).read_bytes()).hexdigest() == expected, name
output.mkdir(parents=True, exist_ok=False)
started = time.monotonic()
manifest = {
    "source_revision": fidelity["revisions"]["timing"],
    "source_sha256": pins,
    "seed": 42,
    "steps": 1000,
    "agents": 500,
    "rebirthing": False,
    "capabilities": 1,
    "iterations": 1,
    "budget_seconds": 1800,
    "scope": "Complete native execution proof only; no performance replication or state replay.",
    "platform": platform.platform(),
    "cpu_affinity": sorted(os.sched_getaffinity(0)),
}
(output / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
(output / "lscpu.json").write_bytes(subprocess.check_output(["lscpu", "--json"]))
for variant in ["seq", "io", "tvar", "tarray"]:
    project = source / "criterion" / f"sugarscape-{variant}"
    with (output / f"{variant}-build.log").open("wb") as build_log:
        subprocess.run(
            ["stack", "build", "--jobs", "2"],
            cwd=project,
            stdout=build_log,
            stderr=subprocess.STDOUT,
            check=True,
            timeout=max(1, 1800 - (time.monotonic() - started)),
        )
    compiler = subprocess.check_output(
        ["stack", "exec", "--", "ghc", "--numeric-version"], cwd=project, text=True
    ).strip()
    assert compiler == "8.4.3", compiler
    install = subprocess.check_output(["stack", "path", "--local-install-root"], cwd=project, text=True).strip()
    binary = Path(install) / "bin" / f"sugarscape-{variant}"
    benchmark = "sugarscape-seq-singlecore/500" if variant == "seq" else f"sugarscape-{variant}-normal:1/500"
    runtime_args = [] if variant == "seq" else ["+RTS", "-N1", "-RTS"]
    names = subprocess.check_output([str(binary), "--list", *runtime_args], cwd=project, text=True).splitlines()
    assert benchmark in names, names
    command = [str(binary), "--iters", "1", "--match", "prefix", benchmark, *runtime_args]
    folder = output / variant
    folder.mkdir()
    record = {
        "variant": variant,
        "benchmark": benchmark,
        "command": command,
        "binary_sha256": hashlib.sha256(binary.read_bytes()).hexdigest(),
        "compiler": compiler,
    }
    (folder / "command.json").write_text(json.dumps(record, indent=2) + "\n")
    remaining = 1800 - (time.monotonic() - started)
    assert remaining > 0
    before = time.monotonic()
    with (folder / "stdout.log").open("wb") as stdout, (folder / "stderr.log").open("wb") as stderr:
        result = subprocess.run(command, cwd=project, stdout=stdout, stderr=stderr, timeout=min(600, remaining))
    record["exit_code"] = result.returncode
    record["elapsed_seconds"] = time.monotonic() - before
    (folder / "exit.json").write_text(json.dumps(record, indent=2) + "\n")
    result.check_returncode()
    assert benchmark in (folder / "stdout.log").read_text()
    with (output / "completed.jsonl").open("a") as ledger:
        ledger.write(json.dumps(record) + "\n")
    print(json.dumps(record), flush=True)
(output / "complete.json").write_text(json.dumps({"completed_workflows": 4}) + "\n")
