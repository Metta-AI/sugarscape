"""Audit all 90 native retry processes against frozen source and raw counters."""

import argparse
import hashlib
import json
import random
import re
import statistics
import tarfile
from pathlib import Path

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("run", type=Path)
parser.add_argument("supplement", type=Path)
parser.add_argument("output", type=Path)
args = parser.parse_args()
root = args.run
supplement = args.supplement
assert not args.output.exists()
assets = Path(__file__).resolve().parent
protocol = json.loads((root / "protocol.json").read_text())
assert protocol == json.loads(
    (assets / "results/retry-scaling-launch-2026-10-17/protocol.json").read_text()
)
assert (root / "exit-code.txt").read_text().strip() == "0"
assert json.loads((root / "complete.json").read_text()) == {"completed_processes": 90}
archive = supplement / "source-f5851488.tar.gz"
assert (
    hashlib.sha256(archive.read_bytes()).hexdigest()
    == protocol["source_archive_sha256"]
)
with tarfile.open(archive) as original:
    for name, digest in protocol["source_sha256"].items():
        source = original.extractfile(name).read()
        assert hashlib.sha256(source).hexdigest() == digest
        measured = (supplement / "source" / name).read_bytes()
        if name in [
            f"criterion/sugarscape-{v}/src/Main.hs" for v in ("tvar", "tarray")
        ]:
            variant = Path(name).parts[1].removeprefix("sugarscape-")
            needle = b"\n      let stmStatsFlag = False  -- collects STM statistics. WARNING: reduces performance!"
            assert source.count(needle) == 1
            assert measured == source.replace(
                needle, needle.replace(b"False", b"True "), 1
            )
            assert measured == (root / f"{variant}-Main.hs").read_bytes()
            assert (
                hashlib.sha256(measured).hexdigest()
                == protocol["changes"][variant]["instrumented_sha256"]
            )
        else:
            assert measured == source
for variant in ("tvar", "tarray"):
    record = json.loads((root / f"{variant}-binary.json").read_text())
    assert record["compiler"] == "8.4.3"
    assert (
        hashlib.sha256((supplement / f"sugarscape-{variant}").read_bytes()).hexdigest()
        == record["sha256"]
    )
hardware = json.loads((root / "hardware.json").read_text())
assert len(set(hardware["affinity"])) == len(hardware["affinity"]) == 8
allocated = set()
for item in hardware["cpuset"].strip().split(","):
    endpoints = [int(value) for value in item.split("-")]
    assert 1 <= len(endpoints) <= 2
    allocated.update(range(endpoints[0], endpoints[-1] + 1))
assert allocated == set(hardware["affinity"])
quota, period = hardware["cpu_max"].split()
assert int(period) > 0 and (quota == "max" or int(quota) / int(period) >= 8)
fields = {row["field"]: row["data"] for row in hardware["lscpu"]["lscpu"]}
assert int(fields["Thread(s) per core:"]) == 1
schedule = [
    dict(condition, repetition=rep)
    for condition in protocol["conditions"]
    for rep in range(5)
]
random.Random(20261017).shuffle(schedule)
assert json.loads((root / "schedule.json").read_text()) == schedule
ledger = [
    json.loads(line) for line in (root / "completed.jsonl").read_text().splitlines()
]
assert len(ledger) == len(schedule) == 90
rows = []
for index, condition in enumerate(schedule):
    folder = root / f"run-{index:03d}"
    variant, caps, agents = condition["variant"], condition["caps"], condition["agents"]
    scenario = "rebirthing" if condition["rebirthing"] else "normal"
    benchmark = f"sugarscape-{variant}-{scenario}:{caps}/{agents}"
    command = json.loads((folder / "command.json").read_text())
    assert command["condition"] == condition
    binary = json.loads((root / f"{variant}-binary.json").read_text())["binary"]
    assert command["command"] == [
        binary,
        "--iters",
        "1",
        "--match",
        "prefix",
        benchmark,
        "+RTS",
        f"-N{caps}",
        "-RTS",
    ]
    assert (folder / "exit-code.txt").read_text().strip() == "0"
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
    assert record == ledger[index]
    rows.append(record)
assert len(list(root.glob("run-*"))) == 90
targets = json.loads((assets / "retry-targets.json").read_text())["targets"]
summary = []
for condition in protocol["conditions"]:
    members = [
        row
        for row in rows
        if all(row["condition"][key] == value for key, value in condition.items())
    ]
    assert {row["condition"]["repetition"] for row in members} == set(range(5))
    ratios = [row["ratio"] for row in members]
    (target,) = [
        row
        for row in targets
        if all(row[key] == value for key, value in condition.items())
    ]
    summary.append(
        {
            "condition": condition,
            "processes": 5,
            "paper_ratio": target["reported_ratio"],
            "mean_minus_paper": statistics.mean(ratios) - target["reported_ratio"],
            "ratio_mean": statistics.mean(ratios),
            "ratio_min": min(ratios),
            "ratio_max": max(ratios),
            "ratio_sample_sd": statistics.stdev(ratios),
            "pooled_ratio": sum(row["retries"] for row in members)
            / sum(row["commits"] for row in members),
            "rounded_zero_with_nonzero_retries": sum(
                row["printed_ratio"] == "0.00" and row["retries"] > 0 for row in members
            ),
        }
    )
report = {
    "processes_audited": 90,
    "conditions_audited": 18,
    "model_steps_per_process": 1000,
    "hardware": hardware,
    "conditions": summary,
    "rows": rows,
    "scope": "Full declared retry ensemble on different hardware; five fresh processes per condition are our protocol, not an authenticated paper repetition count. Ratios are retries/commits. No timing or whole-paper verdict.",
}
args.output.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n")
print(json.dumps({"processes_audited": 90, "conditions_audited": 18}))
