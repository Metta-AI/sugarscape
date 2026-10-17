"""Execute original population exporters in bounded, separately recorded processes."""

import argparse
import csv
import hashlib
import json
import os
from pathlib import Path
import random
import subprocess
import time

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("source", type=Path)
parser.add_argument("protocol", type=Path)
parser.add_argument("output", type=Path)
args = parser.parse_args()
source, root = args.source.resolve(), args.output.resolve()
protocol = json.loads(args.protocol.read_text())
assert protocol["phase"] in ["qualification", "full-native"]
manifest_path = source / "observer-manifest.json"
assert (
    hashlib.sha256(manifest_path.read_bytes()).hexdigest()
    == protocol["observer_manifest_sha256"]
)
manifest = json.loads(manifest_path.read_text())
for name, original_digest in manifest["source_sha256"].items():
    digest = (
        manifest["changes"][name]["exporter_sha256"]
        if name in manifest["changes"]
        else original_digest
    )
    assert hashlib.sha256((source / name).read_bytes()).hexdigest() == digest
conditions = protocol["conditions"]
assert len(
    {(c["variant"], c["caps"], c["agents"], c["rebirth"]) for c in conditions}
) == len(conditions)
if protocol["phase"] == "full-native":
    expected = {("seq", 1, 500, False)}
    expected |= {
        (v, c, 500, False) for v in ["io", "tvar", "tarray"] for c in range(1, 9)
    }
    expected |= {
        (v, 1 if v == "seq" else 4, n, True)
        for v in ["seq", "io", "tvar", "tarray"]
        for n in [500, 1000, 1500, 2000, 2500]
    }
    assert {
        (c["variant"], c["caps"], c["agents"], c["rebirth"]) for c in conditions
    } == expected
    assert protocol["repetitions"] == 5
    assert float(os.environ["GMN_CPU_LIMIT"]) == 8
    assert len(os.sched_getaffinity(0)) == 8
else:
    assert conditions == [
        {"variant": "seq", "caps": 1, "agents": 500, "rebirth": False},
        {"variant": "tarray", "caps": 1, "agents": 2500, "rebirth": True},
    ]
    assert protocol["repetitions"] == 1
root.mkdir(parents=True, exist_ok=False)
(root / "protocol.json").write_bytes(args.protocol.read_bytes())
(root / "observer-manifest.json").write_bytes(manifest_path.read_bytes())
(root / "runner.py").write_bytes(Path(__file__).read_bytes())
hardware = {
    "affinity": sorted(os.sched_getaffinity(0)),
    "cpu_max": Path("/sys/fs/cgroup/cpu.max").read_text(),
    "cpuset": Path("/sys/fs/cgroup/cpuset.cpus.effective").read_text(),
    "lscpu": json.loads(subprocess.check_output(["lscpu", "--json"])),
}
(root / "hardware.json").write_text(json.dumps(hardware, indent=2) + "\n")
binaries = {}
for variant in sorted({c["variant"] for c in conditions}):
    project = source / "criterion" / f"sugarscape-{variant}"
    with (root / f"{variant}-build.log").open("wb") as log:
        subprocess.run(
            ["stack", "build", "--jobs", "1"],
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
    binary = Path(install) / "bin" / f"sugarscape-{variant}"
    binaries[variant] = str(binary)
    (root / f"{variant}-binary.json").write_text(
        json.dumps(
            {
                "path": str(binary),
                "sha256": hashlib.sha256(binary.read_bytes()).hexdigest(),
                "compiler": compiler,
            }
        )
        + "\n"
    )
schedule = [
    dict(c, repetition=r) for c in conditions for r in range(protocol["repetitions"])
]
random.Random(protocol["schedule_seed"]).shuffle(schedule)
(root / "schedule.json").write_text(json.dumps(schedule, indent=2) + "\n")
for index, condition in enumerate(schedule):
    folder = root / f"run-{index:03d}"
    folder.mkdir()
    variant = condition["variant"]
    command = [binaries[variant], str(condition["agents"]), str(condition["rebirth"])]
    if variant != "seq":
        command += ["+RTS", f"-N{condition['caps']}", "-RTS"]
    (folder / "command.json").write_text(json.dumps(command) + "\n")
    started = time.monotonic()
    with (
        (folder / "population.csv").open("wb") as out,
        (folder / "stderr.log").open("wb") as err,
    ):
        result = subprocess.run(
            command,
            cwd=folder,
            stdout=out,
            stderr=err,
            timeout=protocol["seconds_per_process"],
        )
    (folder / "exit.json").write_text(
        json.dumps(
            {
                "exit_code": result.returncode,
                "elapsed_seconds": time.monotonic() - started,
            }
        )
        + "\n"
    )
    result.check_returncode()
    assert (folder / "stderr.log").read_bytes() == b""
    with (folder / "population.csv").open() as stream:
        reader = csv.DictReader(stream)
        assert reader.fieldnames == ["T", "PopSize"]
        rows = list(reader)
    assert [float(r["T"]) for r in rows] == list(range(1000))
    population = [int(r["PopSize"]) for r in rows]
    assert all(0 <= n <= condition["agents"] for n in population)
    if not condition["rebirth"]:
        assert all(a >= b for a, b in zip(population[:-1], population[1:], strict=True))
    record = {
        "index": index,
        "condition": condition,
        "observations": len(rows),
        "first": population[0],
        "last": population[-1],
        "files_sha256": {
            p.name: hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(folder.iterdir())
        },
    }
    with (root / "completed.jsonl").open("a") as ledger:
        ledger.write(json.dumps(record) + "\n")
    print(json.dumps(record), flush=True)
(root / "complete.json").write_text(
    json.dumps({"completed_runs": len(schedule), "observations": len(schedule) * 1000})
    + "\n"
)
