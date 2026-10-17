"""Execute regeneration and synchronization paths from reachable full-model states."""

import argparse
import csv
import gzip
import hashlib
import json
from pathlib import Path
import platform
import random

from model import Agent, Model

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("capacity", type=Path)
parser.add_argument("output", type=Path)
args = parser.parse_args()
assert (
    hashlib.sha256(args.capacity.read_bytes()).hexdigest()
    == "55f911e1fa16c9ad1ba1be69cf122e7b2ab7cf5e4aef0131d46bd6963262ad3e"
)
with args.capacity.open() as stream:
    capacity = [int(v) for row in csv.reader(stream) for v in row]
safe_sites = []
for position in range(2500):
    y, x = divmod(position, 50)
    neighbors = [
        position,
        ((y + 1) % 50) * 50 + x,
        ((y - 1) % 50) * 50 + x,
        y * 50 + (x + 1) % 50,
        y * 50 + (x - 1) % 50,
    ]
    if all(capacity[p] == 0 for p in neighbors):
        safe_sites.append(position)
assert len(safe_sites) == 305
safe_set = set(safe_sites)
args.output.mkdir(exist_ok=False)
(args.output / "capacity.csv").write_bytes(args.capacity.read_bytes())
cases = []

for seed, warmup in ((0, 0), (1, 37), (2, 100)):
    randomizer = random.Random(seed)
    positions = randomizer.sample(range(2500), 250)
    agents = [
        Agent(
            p,
            randomizer.randint(1, 6),
            randomizer.randint(1, 4),
            randomizer.randint(5, 25),
            randomizer.randint(60, 100),
        )
        for p in positions
    ]
    model = Model(capacity, agents, capacity, seed)
    records = [{"phase": "initial", "state": model.observation(str(seed), 0)}]

    def warmup_birth(index, occupied):
        position = randomizer.choice(sorted(set(range(2500)) - occupied))
        return Agent(
            position,
            randomizer.randint(1, 6),
            randomizer.randint(1, 4),
            randomizer.randint(5, 25),
            randomizer.randint(60, 100),
        )

    for time in range(1, warmup + 1):
        events = model.step(warmup_birth)
        records.append(
            {
                "phase": "warmup",
                "events": events,
                "state": model.observation(str(seed), time),
            }
        )
    starting_hash = model.state_hash()

    def desert_birth(index, occupied):
        position = model.agents[index].position
        if position not in safe_set or position in occupied:
            position = next(p for p in safe_sites if p not in occupied)
        return Agent(position, 1, 1, 5, 99)

    for time in range(1, 105):
        events = model.step(desert_birth)
        records.append(
            {
                "phase": "regenerate",
                "events": events,
                "state": model.observation(str(seed), warmup + time),
            }
        )
    assert model.sugar == capacity
    assert all(
        a.position in safe_set
        and a.vision == a.metabolism == 1
        and 1 <= a.wealth <= 5
        and 95 <= a.life <= 99
        for a in model.agents
    )
    plans = []
    for agent in model.agents:
        difference = 26 - agent.wealth
        a, b = next(
            (a, b) for a in range(6) for b in range(5) if 5 * a + 6 * b == difference
        )
        cycles = [5] * a + [6] * b
        plans.append(
            {
                "first_death": agent.wealth,
                "cycles": cycles,
                "last_birth_time": agent.wealth + sum(cycles),
            }
        )
    assert all(plan["last_birth_time"] == 26 for plan in plans)
    pending = [list(plan["cycles"]) + [5] for plan in plans]
    sync_positions = [a.position for a in model.agents]

    def synchronize_birth(index, occupied):
        return Agent(sync_positions[index], 1, 1, pending[index].pop(0), 99)

    for time in range(1, 31):
        events = model.step(synchronize_birth)
        records.append(
            {
                "phase": "synchronize",
                "events": events,
                "state": model.observation(str(seed), warmup + 104 + time),
            }
        )
    assert all(not remaining for remaining in pending)
    assert model.sugar == capacity
    assert all(
        a.vision == a.metabolism == a.wealth == 1 and a.life == 95 for a in model.agents
    )
    pristine_hash = model.state_hash()
    target_random = random.Random(99)
    target = [
        Agent(
            p,
            target_random.randint(1, 6),
            target_random.randint(1, 4),
            target_random.randint(5, 25),
            target_random.randint(60, 100),
        )
        for p in target_random.sample(range(2500), 250)
    ]
    target_hash = Model(capacity, target, capacity, 99).state_hash()

    def target_birth(index, occupied):
        agent = target[index]
        return Agent(
            agent.position, agent.vision, agent.metabolism, agent.wealth, agent.life
        )

    events = model.step(target_birth)
    records.append(
        {
            "phase": "target",
            "events": events,
            "state": model.observation(str(seed), warmup + 135),
        }
    )
    assert len(events["newborns"]) == 250 and model.state_hash() == target_hash
    raw = "".join(json.dumps(row) + "\n" for row in records).encode()
    filename = f"case-{seed}.jsonl.gz"
    compressed = gzip.compress(raw, mtime=0)
    (args.output / filename).write_bytes(compressed)
    cases.append(
        {
            "seed": seed,
            "warmup": warmup,
            "states": len(records),
            "starting_state_sha256": starting_hash,
            "pristine_state_sha256": pristine_hash,
            "target_state_sha256": target_hash,
            "controlled_steps": 135,
            "synchronization_plans": plans,
            "trajectory": filename,
            "trajectory_sha256": hashlib.sha256(compressed).hexdigest(),
        }
    )

for source in (Path(__file__), Path(__file__).with_name("model.py")):
    (args.output / source.name).write_bytes(source.read_bytes())
report = {
    "python": platform.python_version(),
    "cases": cases,
    "source_sha256": {
        p.name: hashlib.sha256(p.read_bytes()).hexdigest()
        for p in (Path(__file__), Path(__file__).with_name("model.py"))
    },
    "scope": "Three reachable-state demonstrations of the135step construction, including full random-choice tapes. Universal reachability requires the separate proof.",
}
(args.output / "report.json").write_text(json.dumps(report, indent=2) + "\n")
print(
    json.dumps(
        {
            "cases": len(cases),
            "states": sum(case["states"] for case in cases),
            "controlled_steps_per_case": 135,
        }
    )
)
