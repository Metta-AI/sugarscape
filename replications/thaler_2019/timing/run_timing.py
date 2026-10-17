"""Run the original 45-condition local-machine timing experiment serially."""

import argparse
import hashlib
import json
import os
import random
import re
import subprocess
import tarfile
import time
from pathlib import Path

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("source", type=Path)
parser.add_argument("output", type=Path)
args = parser.parse_args()
source = args.source.resolve()
root = args.output.resolve()
assets = Path(__file__).resolve().parent
assert float(os.environ["GMN_CPU_LIMIT"]) == 8
root.mkdir(parents=True, exist_ok=False)
protocol = json.loads((assets / "protocol.json").read_text())
pins = json.loads((assets / "revision-fidelity.json").read_text())["hashes"]["timing"]
for name, digest in pins.items():
    assert hashlib.sha256((source / name).read_bytes()).hexdigest() == digest, name
binaries = {}
for variant in ["seq", "io", "tvar", "tarray"]:
    project = source / "criterion" / f"sugarscape-{variant}"
    with (root / f"{variant}-build.log").open("wb") as log:
        subprocess.run(
            ["stack", "build", "--jobs", "4"],
            cwd=project,
            stdout=log,
            stderr=subprocess.STDOUT,
            check=True,
            timeout=3600,
        )
    assert (
        subprocess.check_output(["stack", "exec", "--", "ghc", "--numeric-version"], cwd=project, text=True).strip()
        == "8.4.3"
    )
    install = subprocess.check_output(["stack", "path", "--local-install-root"], cwd=project, text=True).strip()
    binaries[variant] = str(Path(install) / "bin" / f"sugarscape-{variant}")
normal = [{"table": 6, "variant": "seq", "caps": 1, "agents": 500, "benchmark": "sugarscape-seq-singlecore/500"}]
normal += [
    {"table": 6, "variant": v, "caps": c, "agents": 500, "benchmark": f"sugarscape-{v}-normal:{c}/500"}
    for v in ["io", "tvar", "tarray"]
    for c in range(1, 9)
]
rebirth = [
    {
        "table": 8,
        "variant": v,
        "caps": 1 if v == "seq" else 4,
        "agents": n,
        "benchmark": f"sugarscape-{v}-rebirthing" + ("" if v == "seq" else ":4") + f"/{n}",
    }
    for v in ["seq", "io", "tvar", "tarray"]
    for n in [500, 1000, 1500, 2000, 2500]
]
scheduler = random.Random(20261017)
scheduler.shuffle(normal)
scheduler.shuffle(rebirth)
schedule = normal + rebirth
hardware = {
    "lscpu": json.loads(subprocess.check_output(["lscpu", "--json"])),
    "affinity": sorted(os.sched_getaffinity(0)),
    "cpu_limit": os.environ["GMN_CPU_LIMIT"],
    "memory_limit": os.environ["GMN_MEMORY_LIMIT_BYTES"],
    "uname": subprocess.check_output(["uname", "-a"], text=True),
    "cgroups": {
        str(p): p.read_text()
        for p in [Path("/sys/fs/cgroup/cpu.max"), Path("/sys/fs/cgroup/cpuset.cpus.effective")]
        if p.exists()
    },
}
manifest = {
    "protocol": protocol,
    "schedule": schedule,
    "hardware": hardware,
    "source_sha256": pins,
    "binary_sha256": {v: hashlib.sha256(Path(p).read_bytes()).hexdigest() for v, p in binaries.items()},
}
(root / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
started = time.monotonic()
completed = []
for ordinal, condition in enumerate(schedule):
    if 36000 - (time.monotonic() - started) < 3600:
        break
    variant = condition["variant"]
    runtime = [] if variant == "seq" else ["+RTS", f"-N{condition['caps']}", "-RTS"]
    names = subprocess.check_output([binaries[variant], "--list", *runtime], text=True).splitlines()
    assert condition["benchmark"] in names, condition
    attempts = []
    for attempt in range(1, 4):
        if 36000 - (time.monotonic() - started) < 3600:
            break
        folder = root / f"{ordinal:02d}-{variant}-{condition['caps']}-{condition['agents']}-attempt{attempt}"
        folder.mkdir()
        command = [
            binaries[variant],
            "--match",
            "prefix",
            condition["benchmark"],
            "--output",
            str(folder / "report.html"),
            "--json",
            str(folder / "report.json"),
            *runtime,
        ]
        (folder / "command.json").write_text(json.dumps(command) + "\n")
        before = time.monotonic()
        with (folder / "stdout.log").open("wb") as log:
            result = subprocess.run(
                command,
                cwd=source / "criterion" / f"sugarscape-{variant}",
                stdout=log,
                stderr=subprocess.STDOUT,
                timeout=3600,
            )
        (folder / "exit.json").write_text(
            json.dumps({"exit_code": result.returncode, "elapsed_seconds": time.monotonic() - before}) + "\n"
        )
        result.check_returncode()
        reports = json.loads(re.search(r"var reports = (.*);", (folder / "report.html").read_text())[1])
        assert len(reports) == 1 and reports[0]["reportName"] == condition["benchmark"]
        report = reports[0]
        iterations = [row[report["reportKeys"].index("iters")] for row in report["reportMeasured"]]
        assert iterations == [1, 2, 3, 4], iterations
        regression = report["reportAnalysis"]["anRegress"][0]
        fit = regression["regRSquare"]["estPoint"]
        record = {
            "ordinal": ordinal,
            "condition": condition,
            "attempt": attempt,
            "r_squared": fit,
            "accepted": fit >= 0.99,
            "report_sha256": hashlib.sha256((folder / "report.html").read_bytes()).hexdigest(),
            "ols_seconds": regression["regCoeffs"]["iters"]["estPoint"],
        }
        attempts.append(record)
        with (root / "attempts.jsonl").open("a") as ledger:
            ledger.write(json.dumps(record) + "\n")
        print(json.dumps(record), flush=True)
        if record["accepted"]:
            break
    completed.append(
        {
            "ordinal": ordinal,
            "condition": condition,
            "attempts": attempts,
            "accepted": any(row["accepted"] for row in attempts),
        }
    )
    (root / "progress.json").write_text(json.dumps(completed, indent=2) + "\n")
    checkpoint = root.parent / f"checkpoint-{ordinal:02d}.tar.gz"
    with tarfile.open(checkpoint, "w:gz") as archive:
        archive.add(root, arcname="results")
    print(
        json.dumps({"checkpoint": str(checkpoint), "sha256": hashlib.sha256(checkpoint.read_bytes()).hexdigest()}),
        flush=True,
    )
(root / "terminal.json").write_text(
    json.dumps(
        {
            "conditions_attempted": len(completed),
            "required": 45,
            "accepted": sum(x["accepted"] for x in completed),
            "complete": len(completed) == 45 and all(x["accepted"] for x in completed),
            "elapsed_seconds": time.monotonic() - started,
        },
        indent=2,
    )
    + "\n"
)
