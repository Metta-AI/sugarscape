"""Audit the complete passive GPU capture; retain unexpected model behavior."""

import argparse
from collections import Counter
import csv
import hashlib
import itertools
import json
from pathlib import Path

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("capture", type=Path)
parser.add_argument("gnu_initial_csv", type=Path)
parser.add_argument("benchmark_csv", type=Path)
parser.add_argument("output", type=Path)
args = parser.parse_args()
root = args.capture
assert int((root / "exit-code.txt").read_text()) == 0
assert (
    hashlib.sha256((root / "main.cu").read_bytes()).hexdigest()
    == "307bb4829ffef97b9eb004bdc59b58282aebd937c0bd4138581753bef711fba4"
)
assets = Path(__file__).resolve().parent
assert json.loads((root / "protocol.json").read_text()) == json.loads(
    (assets / "results/state-observer-launch-2026-10-17/protocol.json").read_text()
)
assert (
    hashlib.sha256(args.gnu_initial_csv.read_bytes()).hexdigest()
    == "360ea5866567d826e971e5eef54f6d1ed881b6d421b2664d95310114c4c6611d"
)
with args.gnu_initial_csv.open() as stream:
    host_cells = [
        {key: int(value) for key, value in row.items()}
        for row in csv.DictReader(stream)
    ]
initial = [row for row in host_cells if row["status"] == 1]
capacities = {(row["x"], row["y"]): row["cell_capacity"] for row in host_cells}
assert len(capacities) == 65536
assert len(initial) == 11264
initial_by_id = {row["id"]: row for row in initial}
assert (
    hashlib.sha256(args.benchmark_csv.read_bytes()).hexdigest()
    == "fbe62ec2afd2fbcb87368c49ed151d08988cdda3647f9f1c733449f6d604dcf9"
)
with args.benchmark_csv.open() as stream:
    benchmark = list(itertools.islice(csv.DictReader(stream), 100))
assert len(benchmark) == 100
assert [int(row["step"]) for row in benchmark] == list(range(100))
assert all(
    row["repetition"] == "0"
    and row["grid_width"] == "256"
    and row["pop_size"] == "65536"
    and row["p_occupation"] == "0.17"
    for row in benchmark
)
with (root / "run/performance_scalingperStep.csv").open() as stream:
    observed_counts = list(csv.DictReader(stream))
assert len(observed_counts) == 100
parity_fields = [
    "repetition",
    "grid_width",
    "pop_size",
    "p_occupation",
    "step",
    "pop_count",
]
assert all(
    [a[key] for key in parity_fields] == [b[key] for key in parity_fields]
    for a, b in zip(observed_counts, benchmark)
)
traces = []
for line in (root / "run/stderr.log").read_text().splitlines():
    if line.startswith("RESOLUTION_TRACE,"):
        traces.append([int(value) for value in line.split(",")[1:]])
assert len(traces) == 100
assert [row[0] for row in traces] == list(range(100))
assert traces[0][1] == 0
assert all(row[2] > row[1] for row in traces)
assert all(a[2] == b[1] for a, b in zip(traces, traces[1:]))
summaries = []
previous_unique = {}
state_path = root / "run/state.csv"
with state_path.open() as stream:
    reader = csv.DictReader(stream)
    assert reader.fieldnames == list(initial[0])
    groups = itertools.groupby(reader, key=lambda row: int(row["step"]))
    for step, group in groups:
        assert step == len(summaries) - 1
        rows = [{key: int(value) for key, value in row.items()} for row in group]
        assert all(0 <= row["x"] < 256 and 0 <= row["y"] < 256 for row in rows)
        assert len({(row["x"], row["y"]) for row in rows}) == len(rows)
        assert all(row["status"] in [1, 2, 3] for row in rows)
        assert all(row["id"] in initial_by_id for row in rows)
        assert all(
            row["cell_capacity"] == capacities[row["x"], row["y"]]
            and -1 <= row["cell_sugar"] <= row["cell_capacity"]
            for row in rows
        )
        statuses = Counter(row["status"] for row in rows)
        ids = Counter(row["id"] for row in rows)
        unique = {row["id"]: row for row in rows if ids[row["id"]] == 1}
        if step == -1:
            assert sorted(rows, key=lambda row: row["id"]) == sorted(
                initial, key=lambda row: row["id"]
            )
        else:
            assert statuses[1] == int(benchmark[step]["pop_count"])
        displacement = Counter()
        for identifier in unique.keys() & previous_unique.keys():
            a, b = previous_unique[identifier], unique[identifier]
            dx, dy = abs(a["x"] - b["x"]), abs(a["y"] - b["y"])
            displacement[max(min(dx, 256 - dx), min(dy, 256 - dy))] += 1
        summaries.append(
            {
                "step": step,
                "active_records": len(rows),
                "status_counts": dict(sorted(statuses.items())),
                "duplicate_ids": {str(k): v for k, v in ids.items() if v > 1},
                "nonpositive_wealth": sum(row["sugar"] <= 0 for row in rows),
                "negative_metabolism": sum(row["metabolism"] < 0 for row in rows),
                "changed_metabolism_from_initial": sum(
                    row["metabolism"] != initial_by_id[row["id"]]["metabolism"]
                    for row in rows
                ),
                "wrapped_chebyshev_displacement": dict(sorted(displacement.items())),
                "resolution_counter": None if step == -1 else traces[step][1:],
            }
        )
        previous_unique = unique
assert len(summaries) == 101
report = {
    "initial_active_records_match_gnu_host": 11264,
    "exact_benchmark_population_matches": 100,
    "snapshots": len(summaries),
    "agent_observations": sum(row["active_records"] for row in summaries),
    "sha256": {
        str(path): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in [state_path, args.gnu_initial_csv, args.benchmark_csv]
    },
    "scope": "Passive capture audit, not independent GPU-rule replay or paper completion. Duplicate IDs are retained and excluded from displacement pairing. Multiple resolution rounds can produce displacement greater than one. Population parity does not prove every internal state is unaffected by instrumentation.",
    "states": summaries,
}
with args.output.open("x") as stream:
    stream.write(json.dumps(report, indent=2) + "\n")
print(json.dumps({key: value for key, value in report.items() if key != "states"}))
