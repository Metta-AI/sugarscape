"""Audit unchanged NetLogo 4.0.4 candidate trajectories and a same-seed replay."""

import argparse
import csv
import hashlib
import json
import math
import re
from pathlib import Path

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("first", type=Path)
parser.add_argument("repeat", type=Path)
parser.add_argument("output", type=Path)
args = parser.parse_args()
reports = []
canonical = []
for root in [args.first, args.repeat]:
    assert json.loads((root / "exit.json").read_text())["exit_code"] == 0
    assert not (root / "stderr.log").read_bytes()
    with (root / "trajectory.csv").open() as stream:
        rows = list(csv.reader(stream))
    assert rows[0] == ["BehaviorSpace Table data (NetLogo 4.0.4)"]
    assert rows[4] == ["min-pxcor", "max-pxcor", "min-pycor", "max-pycor"]
    assert rows[5] == ["-25", "25", "-25", "25"]
    header = rows[6]
    records = [dict(zip(header, row, strict=True)) for row in rows[7:]]
    assert [int(r["[step]"]) for r in records] == list(range(1001))
    assert all(int(r["[run number]"]) == 1 and int(r["ticks"]) == int(r["[step]"]) for r in records)
    assert int(records[0]["count agents"]) == 400
    observations = 0
    previous_ids = set()
    timelines = []
    for record in records:
        stack = []
        states = []
        for token in re.findall(r"\[|\]|[^\s\[\]]+", record[header[-1]]):
            if token == "[":
                entry = []
                if stack:
                    stack[-1].append(entry)
                else:
                    assert not states
                    states = entry
                stack.append(entry)
            elif token == "]":
                stack.pop()
            else:
                stack[-1].append(float(token))
        assert not stack
        assert len(states) == int(record["count agents"])
        assert all(len(a) == 9 and all(math.isfinite(x) for x in a) for a in states)
        ids = {a[0] for a in states}
        assert len(ids) == len(states)
        assert all(
            a[0] == int(a[0]) and -25 <= a[1] <= 25 and -25 <= a[2] <= 25 and a[4] >= 0 and a[5] >= 0 for a in states
        )
        if int(record["[step]"]) > 0:
            assert ids <= previous_ids
        previous_ids = ids
        for i, resource in [(4, "sugar"), (5, "spice")]:
            assert math.isclose(
                sum(a[i] for a in states), float(record[f"sum [{resource}] of agents"]), rel_tol=1e-12, abs_tol=1e-8
            )
        assert all(math.isfinite(float(record[k])) for k in header[:-1])
        observations += len(states)
        timelines.append(
            {
                "time": int(record["ticks"]),
                "population": len(states),
                "agent_sugar": float(record["sum [sugar] of agents"]),
                "agent_spice": float(record["sum [spice] of agents"]),
            }
        )
    canonical.append(rows[:3] + rows[4:])
    reports.append(
        {
            "trajectory_sha256": hashlib.sha256((root / "trajectory.csv").read_bytes()).hexdigest(),
            "summary_records": len(records),
            "agent_observations": observations,
            "populations": {str(t): timelines[t]["population"] for t in [0, 100, 500, 1000]},
            "timeline": timelines,
        }
    )
assert canonical[0] == canonical[1], "Replay differs beyond timestamp metadata"
report = {
    "runs": reports,
    "same_seed_replay_exact_except_timestamp": True,
    "scope": (
        "Unmodified recovered candidate under NetLogo4.0.4 and Java11. "
        "Source identity with Weaver2009 and historicalJava parity unverified; no paper credit."
    ),
}
with args.output.open("x") as f:
    f.write(json.dumps(report, indent=2, allow_nan=False) + "\n")
print(
    json.dumps(
        {
            **{k: v for k, v in report.items() if k != "runs"},
            "runs": [{k: v for k, v in r.items() if k != "timeline"} for r in reports],
        }
    )
)
