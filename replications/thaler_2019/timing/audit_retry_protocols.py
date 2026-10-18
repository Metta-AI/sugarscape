"""Independently audit raw retry counters for the complete six-process control."""

import argparse
from collections import Counter
import hashlib
import json
import math
from pathlib import Path
import statistics

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("run", type=Path)
parser.add_argument("recovery", type=Path)
parser.add_argument("output", type=Path)
args = parser.parse_args()
assert not args.output.exists()
protocol = json.loads((args.run / "protocol.json").read_text())
assert (
    protocol["capabilities"],
    protocol["agents"],
    protocol["steps"],
    protocol["seed"],
) == (32, 500, 1000, 42)
assert protocol["repetitions_per_mode"] == 3
expected_hash = "41574620bf9fbf82c58c7bf1e0774c4554215236b837971053d1a9244039013e"
assert (args.run / "binary-sha256.txt").read_text().split()[0] == expected_hash
recovery_protocol = json.loads((args.recovery / "protocol.json").read_text())
for key in [
    "capabilities",
    "agents",
    "steps",
    "seed",
    "binary_sha256",
    "source_revision",
]:
    assert recovery_protocol[key] == protocol[key]
assert recovery_protocol["mode"] == "single"
results = []
for root, mode, expected_status in [
    (
        args.run,
        "criterion_default",
        {"SERVICE_RESULT": "exit-code", "EXIT_CODE": "exited", "EXIT_STATUS": "1"},
    ),
    (
        args.recovery,
        "single",
        {"SERVICE_RESULT": "success", "EXIT_CODE": "exited", "EXIT_STATUS": "0"},
    ),
]:
    assert (root / "binary-sha256.txt").read_text().split()[0] == expected_hash
    status = dict(
        line.split("=", 1)
        for line in (root / "service-result.txt").read_text().splitlines()
    )
    assert status == expected_status
    schedule = json.loads((root / "runs/schedule.json").read_text())
    records = [
        json.loads(line)
        for line in (root / "runs/completed.jsonl").read_text().splitlines()
    ]
    assert len(records) == 3
    assert Counter((row["mode"], row["repetition"]) for row in records) == Counter(
        (mode, r) for r in range(3)
    )
    for index, record in enumerate(records):
        mode, repetition = schedule[index]
        assert (
            record["index"],
            record["mode"],
            record["repetition"],
            record["exit_code"],
        ) == (index, mode, repetition, 0)
        folder = root / "runs" / f"{index:02d}-{mode}-{repetition}"
        assert (folder / "exit-code.txt").read_text().strip() == "0"
        for name, digest in record["files_sha256"].items():
            assert Path(name).name == name
            assert hashlib.sha256((folder / name).read_bytes()).hexdigest() == digest
        command = json.loads((folder / "command.json").read_text())
        assert command[-3:] == ["+RTS", "-N32", "-RTS"]
        assert Path(command[0]).name == "tarray-retry-binary"
        if mode == "single":
            assert command[1:-3] == [
                "--iters",
                "1",
                "--match",
                "prefix",
                "sugarscape-tarray-normal:32/500",
            ]
        else:
            assert command[1:5] == [
                "--match",
                "prefix",
                "sugarscape-tarray-normal:32/500",
                "--output",
            ]
            assert Path(command[5]).name == "criterion.html"
            assert len(command) == 9 and (folder / "criterion.html").stat().st_size > 0
        expected_files = {"command.json", "exit-code.txt", "stdout.log", "stderr.log"}
        if mode == "criterion_default":
            expected_files.add("criterion.html")
        assert set(record["files_sha256"]) == expected_files
        raw = (folder / "stderr.log").read_text()
        rows = [
            line.split() for line in raw.splitlines() if line.startswith("SugarScape ")
        ]
        assert len(rows) == raw.count("STM transaction statistics (")
        assert len(rows) == len(record["observations"])
        assert (len(rows) == 1) if mode == "single" else (len(rows) >= 2)
        observations = []
        previous_commits = previous_retries = 0
        for row, retained in zip(rows, record["observations"], strict=True):
            assert len(row) == 4
            commits, retries = int(row[1]), int(row[2])
            assert commits > previous_commits and retries >= previous_retries
            ratio = retries / commits
            assert abs(float(row[3]) - ratio) <= 0.005000000001
            increment_commits, increment_retries = (
                commits - previous_commits,
                retries - previous_retries,
            )
            values = {
                "cumulative_commits": commits,
                "cumulative_retries": retries,
                "cumulative_ratio": ratio,
                "printed_ratio": row[3],
                "increment_commits": increment_commits,
                "increment_retries": increment_retries,
                "increment_ratio": increment_retries / increment_commits,
            }
            assert retained == values
            observations.append(values)
            previous_commits, previous_retries = commits, retries
        assert (
            math.isfinite(record["elapsed_seconds"]) and record["elapsed_seconds"] > 0
        )
        results.append(
            {
                "index": index,
                "mode": mode,
                "repetition": repetition,
                "simulations": len(rows),
                "first_ratio": observations[0]["cumulative_ratio"],
                "final_ratio": observations[-1]["cumulative_ratio"],
                "observations": observations,
            }
        )
failed = args.run / "runs/03-single-0"
assert (failed / "exit-code.txt").read_text().strip() == "1"
assert "Invalid option `--iters'" in (failed / "stderr.log").read_text()
assert "STM transaction statistics (" not in (failed / "stderr.log").read_text()
comparison = []
for mode in ["single", "criterion_default"]:
    selected = [row for row in results if row["mode"] == mode]
    values = [row["final_ratio"] for row in selected]
    comparison.append(
        {
            "mode": mode,
            "processes": len(values),
            "simulations": sum(row["simulations"] for row in selected),
            "mean_final_ratio": statistics.mean(values),
            "range_final_ratio": [min(values), max(values)],
            "published_ratio": 0.29,
        }
    )
report = {
    "protocol_sha256": hashlib.sha256(
        (args.run / "protocol.json").read_bytes()
    ).hexdigest(),
    "recovery_protocol_sha256": hashlib.sha256(
        (args.recovery / "protocol.json").read_bytes()
    ).hexdigest(),
    "binary_sha256": expected_hash,
    "processes": results,
    "comparison": comparison,
    "scope": "Complete original-configuration protocol control. Descriptive scheduling and counter-accumulation comparison; instrumented timing is not performance evidence. Historical repetition count remains unknown.",
}
args.output.write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps(comparison))
