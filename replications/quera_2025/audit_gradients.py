"""Audit complete native gradient trajectories and independently recompute differences."""

import csv
import hashlib
import json
import math
from pathlib import Path
import statistics
import sys

root = Path(sys.argv[1])
output = Path(sys.argv[2])
protocol = json.loads((root / "protocol.json").read_text())
assert protocol["seeds"] == [0, 1, 2]
assert protocol["finite_difference_steps"] == [0.001, 0.01]
assert json.loads((root / "exit.json").read_text())["exit_code"] == 0
all_rows = []
source_hashes = {}
for seed in protocol["seeds"]:
    path = root / f"seed-{seed}.csv"
    source_hashes[path.name] = hashlib.sha256(path.read_bytes()).hexdigest()
    with path.open() as stream:
        rows = [
            {key: float(value) for key, value in row.items()}
            for row in csv.DictReader(stream)
        ]
    assert len(rows) == 300
    assert [
        (row["seed"], row["step"], row["parameter"], row["time"]) for row in rows
    ] == [
        (seed, step, parameter, time)
        for step in protocol["finite_difference_steps"]
        for parameter in range(1, 7)
        for time in range(25)
    ]
    assert all(math.isfinite(value) for row in rows for value in row.values())
    for row in rows:
        recomputed = (row["plus"] - row["minus"]) / (2 * row["step"])
        assert math.isclose(row["fd"], recomputed, rel_tol=1e-12, abs_tol=1e-12)
        if row["time"] == 0 and row["parameter"] <= 4:
            assert row["fd"] == 0 and row["ad"] == 0
    for time in range(25):
        assert len({row["primal"] for row in rows if row["time"] == time}) == 1
        for parameter in range(1, 7):
            assert (
                len(
                    {
                        row["ad"]
                        for row in rows
                        if row["time"] == time and row["parameter"] == parameter
                    }
                )
                == 1
            )
    all_rows.extend(rows)
summary = []
for parameter, name in enumerate(protocol["parameters"], 1):
    for step in protocol["finite_difference_steps"]:
        rows = [
            row
            for row in all_rows
            if row["parameter"] == parameter and row["step"] == step
        ]
        initial = [row for row in rows if row["time"] == 0]
        later = [row for row in rows if row["time"] > 0]
        summary.append(
            {
                "parameter": name,
                "step": step,
                "initial_mean_ad": statistics.mean(row["ad"] for row in initial),
                "initial_mean_fd": statistics.mean(row["fd"] for row in initial),
                "initial_max_absolute_difference": max(
                    abs(row["ad"] - row["fd"]) for row in initial
                ),
                "later_mean_absolute_difference": statistics.mean(
                    abs(row["ad"] - row["fd"]) for row in later
                ),
                "later_max_absolute_difference": max(
                    abs(row["ad"] - row["fd"]) for row in later
                ),
            }
        )
output.mkdir(exist_ok=False)
(output / "audit.json").write_text(
    json.dumps(
        {
            "rows": len(all_rows),
            "source_sha256": source_hashes,
            "summary": summary,
            "scope": "Native full-trajectory AD/FD diagnostic. Common-random-number finite differences are independently recomputed. Three seeds do not validate expectation-gradient convergence or reproduce Figure 11.",
        },
        indent=2,
    )
    + "\n"
)
print(json.dumps(summary, indent=2))
