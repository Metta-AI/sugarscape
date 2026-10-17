"""Audit peak-core entry, successful combat and tribe counts as separate diagnostics."""

import argparse
from collections import Counter, defaultdict, deque
import csv
import gzip
import hashlib
import io
import json
from pathlib import Path

from scipy.stats import binomtest

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("runs", type=Path)
parser.add_argument("native_home", type=Path)
parser.add_argument("output", type=Path)
args = parser.parse_args()
assets = Path(__file__).parent / "results/combat-ensembles-2026-10-17"
protocol = json.loads((assets / "protocol.json").read_text())
prior = json.loads((assets / "audit.json").read_text())
assert not prior["prefix_only"] and len(prior["results"]) == 400
reference = {
    (row["variant"], row["case"], row["index"]): row for row in prior["results"]
}
rows = []
for variant in ["instrumented_original", "reward_corrected"]:
    ledger_bytes = (args.runs / variant / "completed.jsonl").read_bytes()
    assert hashlib.sha256(ledger_bytes).hexdigest() == prior["ledger_sha256"][variant]
    ledger = {
        (r["scenario"], r["index"]): r
        for r in map(json.loads, ledger_bytes.splitlines())
    }
    for scenario in ["combat_culture", "combat_rebirth"]:
        for index, seed in enumerate(protocol["seeds"]):
            tables = {}
            if index == 0:
                retained = protocol["retained_first_seed"][variant]
                folder = args.native_home / Path(retained["root"]).relative_to(
                    "/root/sugarscape"
                )
                names = {
                    kind: f"{scenario}.{kind}.csv"
                    for kind in ["agents", "cells", "summary"]
                }
                event_name = f"{scenario}.stderr.log"
                hashes = retained["files_sha256"]
            else:
                record = ledger[(scenario, index)]
                assert record["seed"] == seed and record["steps"] == 1000
                folder = args.runs / variant / scenario / f"{index:03d}-{seed}"
                names = {
                    kind: f"trajectory.{kind}.csv"
                    for kind in ["agents", "cells", "summary"]
                }
                event_name = "stderr.log"
                hashes = record["files_sha256"]
            for kind, name in names.items():
                if index == 0:
                    content = (folder / name).read_bytes()
                else:
                    packed = (folder / (name + ".gz")).read_bytes()
                    assert hashlib.sha256(packed).hexdigest() == hashes[name + ".gz"]
                    content = gzip.decompress(packed)
                assert hashlib.sha256(content).hexdigest() == hashes[name]
                tables[kind] = list(csv.DictReader(io.StringIO(content.decode())))
            previous = reference[(variant, scenario, index)]
            event_bytes = (folder / event_name).read_bytes()
            assert hashlib.sha256(event_bytes).hexdigest() == previous["events_sha256"]
            cells = {
                (int(r["x"]), int(r["y"])): float(r["sugar_capacity"])
                for r in tables["cells"]
                if int(r["time"]) == 0
            }
            assert max(cells.values()) == 4
            unvisited = {point for point, capacity in cells.items() if capacity == 4}
            cores = []
            while unvisited:
                component = {min(unvisited)}
                pending = list(component)
                unvisited.difference_update(component)
                while pending:
                    x, y = pending.pop()
                    for neighbor in [(x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)]:
                        if neighbor in unvisited:
                            component.add(neighbor)
                            unvisited.remove(neighbor)
                            pending.append(neighbor)
                cores.append(component)
            assert len(cores) == 2
            cores.sort(key=lambda core: sum(x + y for x, y in core) / len(core))
            owner = {point: tribe for tribe, core in enumerate(cores) for point in core}
            initial = [r for r in tables["agents"] if int(r["time"]) == 0]
            assert len(initial) == 400
            for agent in initial:
                x, y, tribe = (int(agent[k]) for k in ["x", "y", "tribe"])
                assert (tribe == 0 and x < 20 and y < 20) or (
                    tribe == 1 and x >= 30 and y >= 30
                )
            intruders = []
            observed = set()
            for agent in tables["agents"]:
                time, aid, x, y, tribe = (
                    int(agent[k]) for k in ["time", "id", "x", "y", "tribe"]
                )
                if time % 10:
                    continue
                assert (time, aid) not in observed
                observed.add((time, aid))
                if time > 0 and (x, y) in owner and tribe != owner[(x, y)]:
                    intruders.append(
                        {"time": time, "id": aid, "x": x, "y": y, "tribe": tribe}
                    )
            summaries = tables["summary"]
            assert [int(r["time"]) for r in summaries] == list(range(1001))
            assert [int(r["population"]) for r in summaries] == previous[
                "population_trajectory"
            ]
            assert all(
                int(r["red"]) + int(r["blue"]) == int(r["population"])
                for r in summaries
            )
            disappearances = [
                int(r["time"])
                for r in summaries
                if int(r["population"]) > 0 and min(int(r["red"]), int(r["blue"])) == 0
            ]
            requests = defaultdict(deque)
            core_kills = []
            all_kills = Counter()
            birth_tribes = Counter()
            for line in event_bytes.decode().splitlines():
                values = line.split(",")
                event = dict(
                    zip(protocol["trace_formats"][values[0]], values, strict=True)
                )
                if event["kind"] == "birth":
                    birth_tribes[event["tribe"]] += 1
                elif event["kind"] == "attack":
                    key = tuple(int(event[k]) for k in ["time", "attacker", "victim"])
                    requests[key].append(event)
                elif event["kind"] == "combat":
                    key = tuple(int(event[k]) for k in ["time", "attacker", "victim"])
                    attack = requests[key].popleft()
                    all_kills[str(key[1])] += 1
                    target = int(attack["to_x"]), int(attack["to_y"])
                    tribe = {"Blue": 0, "Red": 1}[attack["attacker_tribe"]]
                    if target in owner and tribe != owner[target]:
                        core_kills.append(
                            {
                                "time": key[0],
                                "attacker": key[1],
                                "victim": key[2],
                                "x": target[0],
                                "y": target[1],
                                "attacker_tribe": tribe,
                            }
                        )
            assert dict(all_kills) == previous["kills_by_attacker"]
            assert sum(birth_tribes.values()) == previous["replacement_births"]
            rows.append(
                {
                    "variant": variant,
                    "scenario": scenario,
                    "index": index,
                    "seed": seed,
                    "peak_core_sizes": [len(c) for c in cores],
                    "replacement_births_by_tribe": dict(birth_tribes),
                    "sampled_enemy_core_agent_observations": len(intruders),
                    "unique_sampled_enemy_core_agents": len(
                        {r["id"] for r in intruders}
                    ),
                    "first_sampled_entry": intruders[:1],
                    "successful_enemy_core_kills": core_kills,
                    "first_tribe_disappearance": disappearances[:1],
                    "final_red": int(summaries[-1]["red"]),
                    "final_blue": int(summaries[-1]["blue"]),
                    "largest_individual_kill_count": previous[
                        "largest_individual_kill_count"
                    ],
                    "first_single_agent_time": previous["first_single_agent_time"],
                }
            )
comparisons = []
for variant in ["instrumented_original", "reward_corrected"]:
    for scenario in ["combat_culture", "combat_rebirth"]:
        subset = [
            r for r in rows if r["variant"] == variant and r["scenario"] == scenario
        ]
        assert len(subset) == 100
        events = {}
        for name in [
            "sampled_enemy_core_agent_observations",
            "successful_enemy_core_kills",
            "first_tribe_disappearance",
        ]:
            successes = sum(bool(r[name]) for r in subset)
            interval = binomtest(successes, 100).proportion_ci(method="exact")
            events[name] = {
                "runs": successes,
                "n": 100,
                "ci95": [interval.low, interval.high],
            }
        comparisons.append(
            {
                "variant": variant,
                "scenario": scenario,
                "events": events,
                "largest_individual_kill_count": max(
                    r["largest_individual_kill_count"] for r in subset
                ),
            }
        )
report = {
    "source_audit_sha256": hashlib.sha256(
        (assets / "audit.json").read_bytes()
    ).hexdigest(),
    "protocol_sha256": hashlib.sha256(
        (assets / "protocol.json").read_bytes()
    ).hexdigest(),
    "trajectories": 400,
    "definition": "Exploratory maximum-capacity connected peak cores. Initial low-coordinate corner is Blue; high-coordinate corner is Red. Agent entries measured every10steps for all seeds; successful attacks measured at every recorded event.",
    "limitations": [
        "Original coordinate aliasing and pre-event agent observation timing remain unchanged.",
        "Culture can change tribe: enemy-color presence alone does not establish physical invasion by an initially opposing agent.",
        "Tribe disappearance can arise through culture conversion and natural deaths; it is not proof of a single warrior killing a tribe.",
        "No absence claim beyond1000steps, no whole-paper verdict, and no new simulation coverage.",
    ],
    "comparisons": comparisons,
    "results": rows,
}
with args.output.open("x") as stream:
    stream.write(json.dumps(report, indent=2) + "\n")
print(json.dumps(comparisons))
