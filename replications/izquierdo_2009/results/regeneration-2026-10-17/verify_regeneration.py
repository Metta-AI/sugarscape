"""Independently replay complete saved regeneration workflows from their choice tapes."""

import argparse
import csv
from functools import cache
import gzip
import hashlib
import json
import math
from pathlib import Path


@cache
def visible_cells(position, vision):
    # Independent geometric enumeration, not the simulator's directional loop.
    y, x = divmod(position, 50)
    cells = []
    for candidate in range(2500):
        row, column = divmod(candidate, 50)
        dy = min(abs(y - row), 50 - abs(y - row))
        dx = min(abs(x - column), 50 - abs(x - column))
        if (dy == 0 or dx == 0) and dx + dy <= vision:
            cells.append((candidate, dx + dy))
    return cells


parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("run", type=Path)
parser.add_argument("output", type=Path)
args = parser.parse_args()
report = json.loads((args.run / "report.json").read_text())
assert set(report["source_sha256"]) == {"model.py", "regenerate.py"}
assert [(case["seed"], case["warmup"]) for case in report["cases"]] == [
    (0, 0),
    (1, 37),
    (2, 100),
]
for name, digest in report["source_sha256"].items():
    assert hashlib.sha256((args.run / name).read_bytes()).hexdigest() == digest
assert (
    hashlib.sha256((args.run / "capacity.csv").read_bytes()).hexdigest()
    == "55f911e1fa16c9ad1ba1be69cf122e7b2ab7cf5e4aef0131d46bd6963262ad3e"
)
with (args.run / "capacity.csv").open() as stream:
    capacity = [int(v) for row in csv.reader(stream) for v in row]
assert len(capacity) == 2500 and set(capacity) == {0, 1, 2, 3, 4}
safe = {p for p in range(2500) if all(capacity[q] == 0 for q, _ in visible_cells(p, 1))}
assert len(safe) == 305
total_states = total_moves = total_births = 0
targets = set()
for case in report["cases"]:
    compressed = (args.run / case["trajectory"]).read_bytes()
    assert hashlib.sha256(compressed).hexdigest() == case["trajectory_sha256"]
    records = [json.loads(line) for line in gzip.decompress(compressed).splitlines()]
    assert len(records) == case["states"] == case["warmup"] + 136
    assert [r["state"]["step"] for r in records] == list(range(len(records)))
    first = records[0]["state"]
    slots = [list(a) for a in first["slots"]]
    sugar = list(first["sugar"])
    assert sugar == capacity and len(slots) == len({a[0] for a in slots}) == 250
    assert all(
        0 <= p < 2500
        and 1 <= v <= 6
        and 1 <= m <= 4
        and 5 <= w <= 25
        and 60 <= life <= 100
        for p, v, m, w, life in slots
    )
    births = harvest = 0
    log_probability = 0.0
    for time, record in enumerate(records):
        state = record["state"]
        if time:
            events = record["events"]
            order = events["activation_order"]
            assert (
                sorted(order) == list(range(250)) and len(events["destinations"]) == 250
            )
            sugar = [min(c, s + 1) for c, s in zip(capacity, sugar)]
            occupied = {a[0] for a in slots}
            dead = set()
            log_probability -= math.lgamma(251)
            for index, chosen in zip(order, events["destinations"]):
                position, vision, metabolism, wealth, life = slots[index]
                available = [
                    (p, d)
                    for p, d in visible_cells(position, vision)
                    if p == position or p not in occupied
                ]
                optimum = max((sugar[p], -d) for p, d in available)
                eligible = {p for p, d in available if (sugar[p], -d) == optimum}
                assert chosen in eligible
                log_probability -= math.log(len(eligible))
                occupied.remove(position)
                collected = sugar[chosen]
                sugar[chosen] = 0
                harvest += collected
                wealth += collected - metabolism
                life -= 1
                slots[index] = [chosen, vision, metabolism, wealth, life]
                if wealth <= 0 or life <= 0:
                    dead.add(index)
                else:
                    occupied.add(chosen)
            replacement = events["replacement_order"]
            assert len(replacement) == len(set(replacement)) == len(events["newborns"])
            assert set(replacement) == dead
            log_probability -= math.lgamma(len(dead) + 1)
            for index, newborn in zip(replacement, events["newborns"]):
                p, v, m, w, life = newborn
                assert p not in occupied and 0 <= p < 2500
                assert (
                    1 <= v <= 6 and 1 <= m <= 4 and 5 <= w <= 25 and 60 <= life <= 100
                )
                log_probability -= math.log((2500 - len(occupied)) * 6 * 4 * 21 * 41)
                slots[index] = list(newborn)
                occupied.add(p)
                births += 1
                if record["phase"] == "regenerate":
                    assert p in safe and [v, m, w, life] == [1, 1, 5, 99]
                elif record["phase"] == "synchronize":
                    assert p in safe and v == m == 1 and w in (5, 6) and life == 99
            total_moves += 250
            total_births += len(dead)
        assert state["slots"] == slots and state["sugar"] == sugar
        assert state["occupants"] == sorted(slots)
        assert state["births"] == births and state["harvest"] == harvest
        assert math.isclose(
            state["log_choice_probability"],
            log_probability,
            rel_tol=1e-12,
            abs_tol=1e-9,
        )
        assert len({a[0] for a in slots}) == 250
        # The stronger joint bound follows from a<=100-life and net gain<=3 per step.
        assert all(a[3] > 0 and a[4] > 0 and a[3] + 3 * a[4] <= 325 for a in slots)
        digest = hashlib.sha256(json.dumps([sugar, sorted(slots)]).encode()).hexdigest()
        assert digest == state["state_sha256"]
        if time == case["warmup"]:
            assert digest == case["starting_state_sha256"]
        if time >= case["warmup"] + 100 and time <= case["warmup"] + 134:
            assert all(a[0] in safe and a[1] == a[2] == 1 for a in slots)
        if time >= case["warmup"] + 104:
            assert sugar == capacity
        if time == case["warmup"] + 134:
            assert all(a[1:] == [1, 1, 1, 95] for a in slots)
            assert digest == case["pristine_state_sha256"]
        total_states += 1
    assert records[-1]["state"]["state_sha256"] == case["target_state_sha256"]
    assert len(records[-1]["events"]["newborns"]) == 250
    targets.add(case["target_state_sha256"])
    for plan in case["synchronization_plans"]:
        assert 1 <= plan["first_death"] <= 5
        assert set(plan["cycles"]) <= {5, 6}
        assert (
            plan["first_death"] + sum(plan["cycles"]) == plan["last_birth_time"] == 26
        )
assert len(targets) == 1
args.output.mkdir(exist_ok=False)
(args.output / "verification.json").write_text(
    json.dumps(
        {
            "cases": len(report["cases"]),
            "states_checked": total_states,
            "movement_decisions_checked": total_moves,
            "replacement_decisions_checked": total_births,
            "agent_observations_checked": total_states * 250,
            "cell_observations_checked": total_states * 2500,
            "shared_target_state_sha256": next(iter(targets)),
            "scope": "Every saved movement/replacement choice and full state replayed independently. Three examples do not replace the general reachability proof.",
        },
        indent=2,
    )
    + "\n"
)
