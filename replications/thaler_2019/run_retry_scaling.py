"""Measure the original STM retry counters across all Table 7 conditions."""

import hashlib
import json
import os
from pathlib import Path
import random
import re
import subprocess
import tarfile

root = Path.cwd()
protocol = json.loads((root / "protocol.json").read_text())
source = root / "source"
source.mkdir()
archive = Path("/root/sugarscape/source-f5851488.tar.gz")
assert (
    hashlib.sha256(archive.read_bytes()).hexdigest()
    == protocol["source_archive_sha256"]
)
with tarfile.open(archive) as packed:
    packed.extractall(source, filter="data")
for name, digest in protocol["source_sha256"].items():
    assert hashlib.sha256((source / name).read_bytes()).hexdigest() == digest
hardware = {
    "affinity": sorted(os.sched_getaffinity(0)),
    "cpu_max": Path("/sys/fs/cgroup/cpu.max").read_text(),
    "cpuset": Path("/sys/fs/cgroup/cpuset.cpus.effective").read_text(),
    "lscpu": json.loads(subprocess.check_output(["lscpu", "--json"])),
}
assert len(hardware["affinity"]) == 8
(root / "hardware.json").write_text(json.dumps(hardware, indent=2) + "\n")
binaries = {}
for variant in ["tvar", "tarray"]:
    project = source / "criterion" / f"sugarscape-{variant}"
    main = project / "src/Main.hs"
    original = main.read_bytes()
    needle = b"\n      let stmStatsFlag = False  -- collects STM statistics. WARNING: reduces performance!"
    assert original.count(needle) == 1
    instrumented = original.replace(needle, needle.replace(b"False", b"True "), 1)
    assert (
        hashlib.sha256(instrumented).hexdigest()
        == protocol["changes"][variant]["instrumented_sha256"]
    )
    main.write_bytes(instrumented)
    (root / f"{variant}-Main.hs").write_bytes(instrumented)
    with (root / f"{variant}-build.log").open("wb") as log:
        subprocess.run(
            ["stack", "build", "--jobs", "4"],
            cwd=project,
            stdout=log,
            stderr=subprocess.STDOUT,
            check=True,
            timeout=900,
        )
    compiler = subprocess.check_output(
        ["stack", "exec", "--", "ghc", "--numeric-version"], cwd=project, text=True
    ).strip()
    assert compiler == "8.4.3"
    install = subprocess.check_output(
        ["stack", "path", "--local-install-root"], cwd=project, text=True
    ).strip()
    binaries[variant] = str(Path(install) / "bin" / f"sugarscape-{variant}")
    (root / f"{variant}-binary.json").write_text(
        json.dumps(
            {
                "binary": binaries[variant],
                "sha256": hashlib.sha256(
                    Path(binaries[variant]).read_bytes()
                ).hexdigest(),
                "compiler": compiler,
            }
        )
        + "\n"
    )
schedule = [
    dict(condition, repetition=repetition)
    for condition in protocol["conditions"]
    for repetition in range(protocol["process_repetitions"])
]
random.Random(protocol["schedule_seed"]).shuffle(schedule)
(root / "schedule.json").write_text(json.dumps(schedule, indent=2) + "\n")
for index, condition in enumerate(schedule):
    variant, caps = condition["variant"], condition["caps"]
    scenario = "rebirthing" if condition["rebirthing"] else "normal"
    benchmark = f"sugarscape-{variant}-{scenario}:{caps}/{condition['agents']}"
    folder = root / f"run-{index:03d}"
    folder.mkdir()
    command = [
        binaries[variant],
        "--iters",
        "1",
        "--match",
        "prefix",
        benchmark,
        "+RTS",
        f"-N{caps}",
        "-RTS",
    ]
    (folder / "command.json").write_text(
        json.dumps({"condition": condition, "command": command}) + "\n"
    )
    with (
        (folder / "stdout.log").open("wb") as stdout,
        (folder / "stderr.log").open("wb") as stderr,
    ):
        result = subprocess.run(
            command,
            cwd=source / "criterion" / f"sugarscape-{variant}",
            stdout=stdout,
            stderr=stderr,
            timeout=300,
        )
    (folder / "exit-code.txt").write_text(str(result.returncode) + "\n")
    result.check_returncode()
    assert (folder / "stdout.log").read_text().strip() == f"benchmarking {benchmark}"
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
    with (root / "completed.jsonl").open("a") as ledger:
        ledger.write(json.dumps(record) + "\n")
    print(json.dumps(record), flush=True)
(root / "complete.json").write_text(
    json.dumps({"completed_processes": len(schedule)}) + "\n"
)
