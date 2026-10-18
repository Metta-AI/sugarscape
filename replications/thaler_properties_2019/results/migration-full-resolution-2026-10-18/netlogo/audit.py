"""Audit native migration trajectories and observer noninterference."""

import csv
import hashlib
import json
import math
import re
import sys
from pathlib import Path

root, output = map(Path, sys.argv[1:])
qualification = json.loads((root / "qualification.json").read_text())
protocol = json.loads((root / "protocol.json").read_text())
for name, digest in qualification["files_sha256"].items():
    assert hashlib.sha256((root / name).read_bytes()).hexdigest() == digest
assert (
    hashlib.sha256((root / "run.py").read_bytes()).hexdigest()
    == protocol["runner_sha256"]
)
reports = {}
populations = {}
for name in protocol["cases"]:
    folder = root / name
    assert json.loads((folder / "exit.json").read_text())["exit_code"] == 0
    assert not (folder / "stderr.log").read_bytes()
    with (folder / "trajectory.csv").open() as stream:
        rows = list(csv.reader(stream))
    assert rows[0] == ["BehaviorSpace Table data (NetLogo 4.0.4)"]
    assert rows[5] == ["-25", "25", "-25", "25"]
    records = [dict(zip(rows[6], row, strict=True)) for row in rows[7:]]
    assert [int(row["ticks"]) for row in records] == list(range(1001))
    assert [int(row["[step]"]) for row in records] == list(range(1001))
    populations[name] = [int(row["count agents"]) for row in records]
    assert populations[name][0] == 400
    if name == "preset2-plain":
        continue
    count = 0
    profiles = []
    previous_ids = set(range(400))
    initial_metabolisms = {}
    for step, record in enumerate(records):
        states = [
            [float(value) for value in chunk.split()]
            for chunk in re.findall(r"\[([^\[\]]+)\]", record["observed-agent-states"])
        ]
        assert len(states) == int(record["count agents"])
        assert all(
            len(agent) == 9 and all(map(math.isfinite, agent)) for agent in states
        )
        ids = {agent[0] for agent in states}
        assert len(ids) == len(states) and ids <= previous_ids
        previous_ids = ids
        assert len({(agent[1], agent[2]) for agent in states}) == len(states)
        maximum_vision = 15 if name == "vision15-observed" else 10
        assert all(
            -25 <= a[1] <= 25
            and -25 <= a[2] <= 25
            and a[3] == step
            and a[4] >= 0
            and a[5] >= 0
            and 0 <= a[6] <= 4
            and 1 <= a[8] <= maximum_vision
            for a in states
        )
        for index, resource in [(4, "sugar"), (5, "spice")]:
            assert math.isclose(
                sum(a[index] for a in states),
                float(record[f"observed-agent-{resource}"]),
                rel_tol=1e-12,
                abs_tol=1e-8,
            )
        if step == 0:
            assert all(
                -25 <= a[1] <= -3 and -25 <= a[2] <= -3 and 5 <= a[4] <= 25
                for a in states
            )
            initial_metabolisms = {
                str(m): sum(a[6] == m for a in states) for m in range(5)
            }
        diagonal = [0] * 101
        for agent in states:
            diagonal[int(agent[1] + agent[2]) + 50] += 1
        profiles.append({"step": step, "diagonal_counts": diagonal})
        count += len(states)
    reports[name] = {
        "summary_records": len(records),
        "agent_observations": count,
        "initial_metabolism_counts": initial_metabolisms,
        "final_population": populations[name][-1],
        "profiles": profiles,
    }
assert populations["preset2-plain"] == populations["preset2-observed"]
with output.open("x") as stream:
    json.dump(
        {"observer_population_parity_frames": 1001, "cases": reports},
        stream,
        indent=2,
        allow_nan=False,
    )
print(
    json.dumps(
        {
            name: {key: value for key, value in report.items() if key != "profiles"}
            for name, report in reports.items()
        }
    )
)
