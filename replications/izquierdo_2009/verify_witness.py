"""Check complete saved witness trajectories independently of the simulator."""

import argparse
import csv
import hashlib
import json
import math
from pathlib import Path

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("run", type=Path)
parser.add_argument("output", type=Path)
args = parser.parse_args()
report = json.loads((args.run / "report.json").read_text())
capacity = [
    int(value)
    for row in csv.reader((args.run / "capacity.csv").open())
    for value in row
]
assert len(capacity) == 2500 and min(capacity) == 0 and max(capacity) == 4
rows = [
    json.loads(line)
    for line in (args.run / "trajectory.jsonl").read_text().splitlines()
]
assert len(rows) == 18
groups = {
    name: [row for row in rows if row["experiment"] == name]
    for name in ("return-5", "return-6", "initial-reachability")
}
target = report["return_paths"][0]["return_state_sha256"]
for name, path in groups.items():
    period = 5 if name == "return-5" else 6 if name == "return-6" else 4
    assert [row["step"] for row in path] == list(range(period + 1))
    initial_positions = [agent[0] for agent in path[0]["occupants"]]
    assert len(initial_positions) == len(set(initial_positions)) == 250
    for position in initial_positions:
        y, x = divmod(position, 50)
        neighborhood = [
            position,
            ((y + 1) % 50) * 50 + x,
            ((y - 1) % 50) * 50 + x,
            y * 50 + (x + 1) % 50,
            y * 50 + (x - 1) % 50,
        ]
        assert all(capacity[p] == 0 for p in neighborhood)
    for time, row in enumerate(path):
        assert row["sugar"] == capacity and row["harvest"] == 0
        assert [agent[0] for agent in row["occupants"]] == initial_positions
        if name == "initial-reachability":
            wealth, life, births = 5 - time, 99 - time, 0
        elif time == 0:
            wealth, life, births = 1, 95, 0
        else:
            wealth, life, births = period - (time - 1), (94 + period) - (time - 1), 250
        assert row["births"] == births
        assert all(agent[1:] == [1, 1, wealth, life] for agent in row["occupants"])
        assert math.isfinite(row["log_choice_probability"])
        digest = hashlib.sha256(
            json.dumps([row["sugar"], row["occupants"]]).encode()
        ).hexdigest()
        assert digest == row["state_sha256"]
    assert path[-1]["state_sha256"] == target
    if name != "initial-reachability":
        assert path[0]["state_sha256"] == target
assert [row["period"] for row in report["return_paths"]] == [5, 6]
assert math.gcd(5, 6) == report["return_period_gcd"] == 1
args.output.mkdir(exist_ok=False)
(args.output / "verification.json").write_text(
    json.dumps(
        {
            "saved_states_checked": len(rows),
            "agent_observations_checked": len(rows) * 250,
            "cell_observations_checked": len(rows) * 2500,
            "return_periods": [5, 6],
            "common_state_sha256": target,
            "trajectory_sha256": hashlib.sha256(
                (args.run / "trajectory.jsonl").read_bytes()
            ).hexdigest(),
            "scope": "Independent arithmetic, topology and full-state checks on the saved witnesses; no proof of global irreducibility.",
        },
        indent=2,
    )
    + "\n"
)
