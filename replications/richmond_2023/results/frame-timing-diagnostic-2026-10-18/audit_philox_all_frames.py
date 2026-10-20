"""Reconstruct metabolism, death, resource accounting and transfers from native states.

Observed destinations are inputs: this does not independently reproduce GPU random
choices, conflict winners, or the order of within-step resolution rounds.
"""

import argparse
import csv
import gzip
import hashlib
import itertools
import json
from pathlib import Path

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("initial", type=Path)
parser.add_argument("states", type=Path)
parser.add_argument("output", type=Path)
args = parser.parse_args()
assert (
    hashlib.sha256(args.initial.read_bytes()).hexdigest()
    == "8d2bbe429ab27b161cc645f2ceab9df70b4fc7e4be1c67718a4e6dba638e1158"
)
assert (
    hashlib.sha256(args.states.read_bytes()).hexdigest()
    == "c713fc3663d5d87f8268964c3cc422cf498e38294477bde89229bb615a71adad"
)
with args.initial.open() as stream:
    cells = {
        (int(r["x"]), int(r["y"])): {k: int(v) for k, v in r.items()}
        for r in csv.DictReader(stream)
    }
assert len(cells) == 65536
sugar = {p: r["cell_sugar"] for p, r in cells.items()}
previous = {r["id"]: r for r in cells.values() if r["status"] != 0}
reports = []
snapshots = [{"step": -1, "environment_sugar": list(sugar.values())}]
with args.states.open() as stream:
    for step, group in itertools.groupby(
        csv.DictReader(stream), key=lambda r: int(r["step"])
    ):
        rows = [{k: int(v) for k, v in r.items()} for r in group]
        current = {r["id"]: r for r in rows}
        assert len(current) == len(rows)
        if step == -1:
            assert current == previous
            continue
        assert step == len(reports)
        occupied = {(r["x"], r["y"]) for r in previous.values()}
        wealth = {}
        for identifier, r in previous.items():
            pos = r["x"], r["y"]
            wealth[identifier] = r["sugar"] + max(sugar[pos], 0) - r["metabolism"]
            if sugar[pos] > 0:
                sugar[pos] = -1
            if wealth[identifier] == 0:
                occupied.remove(pos)
                sugar[pos] = 0
        dead = {i for i, w in wealth.items() if w == 0}
        assert set(current) == set(previous) - dead
        for pos in sugar:
            if pos not in occupied:
                sugar[pos] = min(sugar[pos] + 1, cells[pos]["cell_capacity"])
        moved = {
            i
            for i, r in current.items()
            if (r["x"], r["y"]) != (previous[i]["x"], previous[i]["y"])
        }
        sources = {(previous[i]["x"], previous[i]["y"]) for i in moved}
        for i, r in current.items():
            pos = r["x"], r["y"]
            old = previous[i]
            if i in moved:
                dx, dy = abs(r["x"] - old["x"]), abs(r["y"] - old["y"])
                assert max(min(dx, 256 - dx), min(dy, 256 - dy)) == 1
                assert r["metabolism"] == -1 and r["status"] == 1
                assert r["sugar"] == (0 if pos in sources else sugar[pos]) - 1
                assert pos not in occupied or pos in sources
            else:
                assert r["metabolism"] == old["metabolism"]
                assert r["sugar"] == wealth[i]
        for pos in sources:
            sugar[pos] = 0
        for i in moved:
            sugar[current[i]["x"], current[i]["y"]] = -1
        assert all(r["cell_sugar"] == sugar[r["x"], r["y"]] for r in rows)
        reports.append(
            {
                "step": step,
                "active": len(current),
                "deaths": len(dead),
                "moves": len(moved),
                "stays": len(current) - len(moved),
                "diagonal_moves": sum(
                    current[i]["x"] != previous[i]["x"]
                    and current[i]["y"] != previous[i]["y"]
                    for i in moved
                ),
                "negative_wealth_after_metabolism_survivors": sum(
                    w < 0 for w in wealth.values()
                ),
                "unresolved": sum(r["status"] == 3 for r in rows),
            }
        )
        snapshots.append({"step": step, "environment_sugar": list(sugar.values())})
        previous = current
assert len(reports) == 100
report = {
    "steps": 100,
    "post_step_agent_observations": sum(r["active"] for r in reports),
    "moves": sum(r["moves"] for r in reports),
    "deaths": sum(r["deaths"] for r in reports),
    "scope": __doc__,
    "observations": reports,
}
with gzip.open(args.output.with_suffix(".snapshots.json.gz"), "xt") as stream:
    json.dump(
        {"coordinate_order": "x major, ascending y", "snapshots": snapshots}, stream
    )
with args.output.open("x") as stream:
    stream.write(json.dumps(report, indent=2) + "\n")
print(json.dumps({k: v for k, v in report.items() if k != "observations"}))
