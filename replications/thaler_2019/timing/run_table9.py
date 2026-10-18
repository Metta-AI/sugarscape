"""Run all six Table9 timings, then thirty separately instrumented retry processes."""

import argparse
import hashlib
import json
import os
import random
import re
import shutil
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
assert len(os.sched_getaffinity(0)) == 64
root.mkdir(parents=True, exist_ok=False)
protocol = json.loads((assets / "table9-protocol.json").read_text())
pins = json.loads((assets / "revision-fidelity.json").read_text())["hashes"]["timing"]
for name, digest in pins.items():
    assert hashlib.sha256((source / name).read_bytes()).hexdigest() == digest, name
binaries = {}
for variant in ["tarray"]:
    project = source / "criterion" / f"sugarscape-{variant}"
    with (root / f"{variant}-build.log").open("wb") as log:
        subprocess.run(
            ["stack", "build", "--jobs", "4"],
            cwd=project,
            stdout=log,
            stderr=subprocess.STDOUT,
            check=True,
            timeout=1200,
        )
    assert (
        subprocess.check_output(
            ["stack", "exec", "--", "ghc", "--numeric-version"], cwd=project, text=True
        ).strip()
        == "8.4.3"
    )
    install = subprocess.check_output(
        ["stack", "path", "--local-install-root"], cwd=project, text=True
    ).strip()
    retained_binary = root / f"{variant}-timing-binary"
    shutil.copy2(Path(install) / "bin" / f"sugarscape-{variant}", retained_binary)
    binaries[variant] = str(retained_binary)
schedule = json.loads((assets / "table9-preflight.json").read_text())["conditions"]
schedule = [
    dict(c, table=9, caps=c["capabilities"], scenario=c["variant"], variant="tarray")
    for c in schedule
]
random.Random(20261018).shuffle(schedule)
hardware = {
    "lscpu": json.loads(subprocess.check_output(["lscpu", "--json"])),
    "affinity": sorted(os.sched_getaffinity(0)),
    "cpu_limit": 64,
    "meminfo": Path("/proc/meminfo").read_text(),
    "uname": subprocess.check_output(["uname", "-a"], text=True),
    "cgroups": {
        str(p): p.read_text()
        for p in [
            Path("/sys/fs/cgroup/cpu.max"),
            Path("/sys/fs/cgroup/cpuset.cpus.effective"),
        ]
        if p.exists()
    },
}
for cgroup_path, value in hardware["cgroups"].items():
    if cgroup_path.endswith("/cpu.max"):
        quota, period = value.split()
        assert quota == "max" or int(quota) / int(period) >= 64
cpu_fields = {r["field"]: r["data"] for r in hardware["lscpu"]["lscpu"]}
assert int(cpu_fields["CPU(s):"]) == 64
assert int(cpu_fields["Thread(s) per core:"]) == 2
manifest = {
    "protocol": protocol,
    "schedule": schedule,
    "hardware": hardware,
    "source_sha256": pins,
    "binary_sha256": {
        v: hashlib.sha256(Path(p).read_bytes()).hexdigest() for v, p in binaries.items()
    },
}
(root / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
started = time.monotonic()
completed = []
for ordinal, condition in enumerate(schedule):
    if 7200 - (time.monotonic() - started) < 1200:
        break
    variant = condition["variant"]
    runtime = [] if variant == "seq" else ["+RTS", f"-N{condition['caps']}", "-RTS"]
    names = subprocess.check_output(
        [binaries[variant], "--list", *runtime], text=True
    ).splitlines()
    assert condition["benchmark"] in names, condition
    attempts = []
    for attempt in range(1, 4):
        if 7200 - (time.monotonic() - started) < 1200:
            break
        folder = (
            root
            / f"{ordinal:02d}-{variant}-{condition['caps']}-{condition['agents']}-attempt{attempt}"
        )
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
                timeout=1200,
            )
        (folder / "exit.json").write_text(
            json.dumps(
                {
                    "exit_code": result.returncode,
                    "elapsed_seconds": time.monotonic() - before,
                }
            )
            + "\n"
        )
        result.check_returncode()
        reports = json.loads(
            re.search(r"var reports = (.*);", (folder / "report.html").read_text())[1]
        )
        assert len(reports) == 1 and reports[0]["reportName"] == condition["benchmark"]
        report = reports[0]
        iterations = [
            row[report["reportKeys"].index("iters")] for row in report["reportMeasured"]
        ]
        assert iterations == [1, 2, 3, 4], iterations
        regression = report["reportAnalysis"]["anRegress"][0]
        fit = regression["regRSquare"]["estPoint"]
        record = {
            "ordinal": ordinal,
            "condition": condition,
            "attempt": attempt,
            "r_squared": fit,
            "accepted": fit >= 0.99,
            "report_sha256": hashlib.sha256(
                (folder / "report.html").read_bytes()
            ).hexdigest(),
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
        json.dumps(
            {
                "checkpoint": str(checkpoint),
                "sha256": hashlib.sha256(checkpoint.read_bytes()).hexdigest(),
            }
        ),
        flush=True,
    )
(root / "timing-terminal.json").write_text(
    json.dumps(
        {
            "conditions_attempted": len(completed),
            "required": 6,
            "accepted": sum(x["accepted"] for x in completed),
            "complete": len(completed) == 6 and all(x["accepted"] for x in completed),
            "elapsed_seconds": time.monotonic() - started,
        },
        indent=2,
    )
    + "\n"
)

# Timing and retry counters must use separate executables.
project = source / "criterion/sugarscape-tarray"
main = project / "src/Main.hs"
original = main.read_bytes()
needle = b"\n      let stmStatsFlag = False  -- collects STM statistics. WARNING: reduces performance!"
assert original.count(needle) == 1
instrumented = original.replace(needle, needle.replace(b"False", b"True "), 1)
assert (
    hashlib.sha256(instrumented).hexdigest()
    == "cdea6f017ef1b91b4a1d6dd8590f4afc1c18b96694c57f612b7dae15d11b3b3f"
)
main.write_bytes(instrumented)
(root / "retry-Main.hs").write_bytes(instrumented)
with (root / "retry-build.log").open("wb") as log:
    subprocess.run(
        ["stack", "build", "--jobs", "4"],
        cwd=project,
        stdout=log,
        stderr=subprocess.STDOUT,
        check=True,
        timeout=900,
    )
retry_binary = root / "tarray-retry-binary"
shutil.copy2(Path(install) / "bin/sugarscape-tarray", retry_binary)
(root / "retry-binary-sha256.txt").write_text(
    hashlib.sha256(retry_binary.read_bytes()).hexdigest() + "\n"
)
retry_schedule = [dict(c, repetition=r) for c in schedule for r in range(5)]
random.Random(20261019).shuffle(retry_schedule)
(root / "retry-schedule.json").write_text(json.dumps(retry_schedule, indent=2) + "\n")
retry_records = []
for index, condition in enumerate(retry_schedule):
    if 9000 - (time.monotonic() - started) < 300:
        break
    folder = root / f"retry-{index:02d}"
    folder.mkdir()
    command = [
        str(retry_binary),
        "--iters",
        "1",
        "--match",
        "prefix",
        condition["benchmark"],
        "+RTS",
        f"-N{condition['caps']}",
        "-RTS",
    ]
    (folder / "command.json").write_text(json.dumps(command) + "\n")
    with (
        (folder / "stdout.log").open("wb") as stdout,
        (folder / "stderr.log").open("wb") as stderr,
    ):
        result = subprocess.run(
            command, cwd=project, stdout=stdout, stderr=stderr, timeout=300
        )
    (folder / "exit-code.txt").write_text(str(result.returncode) + "\n")
    result.check_returncode()
    assert (
        folder / "stdout.log"
    ).read_text().strip() == f"benchmarking {condition['benchmark']}"
    log = (folder / "stderr.log").read_text()
    counters = re.findall(
        r"^SugarScape\s+(\d+)\s+(\d+)\s+(\d+\.\d+)\s*$", log, re.MULTILINE
    )
    assert len(counters) == log.count("STM transaction statistics (") == 1
    commits, retries, printed = counters[0]
    commits, retries = int(commits), int(retries)
    assert commits > 0 and f"{retries / commits:.2f}" == printed
    record = {
        "index": index,
        "condition": condition,
        "commits": commits,
        "retries": retries,
        "ratio": retries / commits,
        "printed_ratio": printed,
        "files_sha256": {
            p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in folder.iterdir()
        },
    }
    with (root / "retry-completed.jsonl").open("a") as ledger:
        ledger.write(json.dumps(record) + "\n")
    retry_records.append(record)
    print(json.dumps(record), flush=True)
(root / "terminal.json").write_text(
    json.dumps(
        {
            "timing_conditions_accepted": sum(c["accepted"] for c in completed),
            "timing_conditions_required": 6,
            "retry_processes_completed": len(retry_records),
            "retry_processes_required": 30,
            "complete": len(completed) == 6
            and all(c["accepted"] for c in completed)
            and len(retry_records) == 30,
        },
        indent=2,
    )
    + "\n"
)
