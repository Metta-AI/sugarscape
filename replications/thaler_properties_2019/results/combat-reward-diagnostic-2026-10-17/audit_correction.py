"""Audit reward correction, unchanged controls, matched initialization and event accounting."""

import argparse
import csv
import hashlib
import json
import math
from collections import Counter
from pathlib import Path

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("root", type=Path)
parser.add_argument("original", type=Path)
parser.add_argument("output", type=Path)
parser.add_argument("historical_trace", type=Path)
args = parser.parse_args()
protocol = json.loads((args.root / "protocol.json").read_text())
assert json.loads((args.root / "complete.json").read_text()) == {"completed_cases": 5}
for name, digest in protocol["original"]["source_sha256"].items():
    assert hashlib.sha256((args.original / "source" / name).read_bytes()).hexdigest() == digest
    assert (
        hashlib.sha256((args.root / "source" / name).read_bytes()).hexdigest()
        == protocol["patched_source_sha256"][name]
    )
changed = sorted(
    name
    for name, digest in protocol["original"]["source_sha256"].items()
    if protocol["patched_source_sha256"][name] != digest
)
assert changed == protocol["changed_files"]
for name, digest in protocol["reference_trace_source_sha256"].items():
    assert hashlib.sha256((args.historical_trace / "source" / name).read_bytes()).hexdigest() == digest
assert [
    name
    for name, digest in protocol["reference_trace_source_sha256"].items()
    if protocol["patched_source_sha256"][name] != digest
] == ["src/SugarScape/Agent/Move.hs"]
old_move = (args.historical_trace / "source/src/SugarScape/Agent/Move.hs").read_bytes()
anchor = b"        let victimId = sugEnvOccId (fromJust $ sugEnvSiteOccupier site)"
addition = (
    b"        updateAgentState (\\s -> s { sugAgSugarLevel = sugAgSugarLevel s + combatWealth })\n"
    b"        updateSiteOccupied\n"
    b"\n"
)
assert old_move.count(anchor) == 1
assert (args.root / "source/src/SugarScape/Agent/Move.hs").read_bytes() == old_move.replace(anchor, addition + anchor)

assert (
    hashlib.sha256((args.original / "Observe.hs").read_bytes()).hexdigest() == protocol["original"]["observer_sha256"]
)
assert (args.root / "Observe.hs").read_bytes() == (args.original / "Observe.hs").read_bytes()
assert hashlib.sha256((args.original / "observe").read_bytes()).hexdigest() == protocol["original"]["binary_sha256"]
results = []
for label, constructor, steps in protocol["cases"]:
    hashes = {}
    equality = {}
    for suffix in ["agents.csv", "summary.csv", "cells.csv", "trades.csv", "scenario.txt"]:
        reference = args.root / "reference" / f"{label}.{suffix}"
        traced = args.root / "traced" / f"{label}.{suffix}"
        assert reference.read_bytes() == (args.historical_trace / "reference" / f"{label}.{suffix}").read_bytes()
        equality[suffix] = reference.read_bytes() == traced.read_bytes()
        if label in ["wealth", "carrying", "trading"] or suffix == "scenario.txt":
            assert equality[suffix], (label, suffix)
        if suffix.endswith(".csv"):
            original_rows = list(csv.DictReader(reference.open()))
            corrected_rows = list(csv.DictReader(traced.open()))
            assert [r for r in original_rows if r["time"] == "0"] == [r for r in corrected_rows if r["time"] == "0"]
        hashes[suffix] = {
            "original": hashlib.sha256(reference.read_bytes()).hexdigest(),
            "corrected": hashlib.sha256(traced.read_bytes()).hexdigest(),
        }
    assert not (args.root / "reference" / f"{label}.stderr.log").read_bytes()
    summaries = list(csv.DictReader((args.root / "traced" / f"{label}.summary.csv").open()))
    assert [int(r["time"]) for r in summaries] == list(range(steps + 1))
    assert all(math.isfinite(float(v)) for row in summaries for v in row.values())
    agents = {t: set() for t in range(steps + 1)}
    for row in csv.DictReader((args.root / "traced" / f"{label}.agents.csv").open()):
        assert all(math.isfinite(float(v)) for k, v in row.items() if k != "culture")
        t = int(row["time"])
        aid = int(row["id"])
        assert aid not in agents[t]
        agents[t].add(aid)
    assert all(len(ids) == int(summaries[t]["population"]) for t, ids in agents.items())
    raw_events = (args.root / "traced" / f"{label}.stderr.log").read_bytes()
    events = list(csv.reader(raw_events.decode().splitlines()))
    grouped = {t: [] for t in range(steps)}
    times = []
    for fields in events:
        schema = protocol["trace_formats"][fields[0]]
        assert len(fields) == len(schema)
        record = dict(zip(schema, fields, strict=True))
        t = int(record["time"])
        times.append(t)
        grouped[t].append(record)
        for key, value in record.items():
            if key == "kind":
                continue
            if key.endswith("tribe"):
                assert value in ["Red", "Blue"]
            elif key == "spice_enabled":
                assert value in ["True", "False"]
            else:
                assert math.isfinite(float(value))
    assert times == sorted(times)
    active = set(agents[0])
    ever = set(active)
    deaths = {}
    births = {}
    attacks = Counter()
    combats = Counter()
    totals = Counter()
    reward_rows = []
    previous = None
    for time in range(steps):
        for event in grouped[time]:
            kind = event["kind"]
            totals[kind] += 1
            if kind == "attack":
                key = (time, int(event["attacker"]), int(event["victim"]))
                attacks[key] += 1
                before = float(event["attacker_wealth_before"])
                after = float(event["attacker_wealth_after_harvest"])
                harvest = float(event["harvest"])
                reward = float(event["computed_combat_reward"])
                reward_rows.append(
                    {
                        "time": time,
                        "attacker": key[1],
                        "victim": key[2],
                        "before": before,
                        "after": after,
                        "harvest": harvest,
                        "reward": reward,
                        "harvest_only": math.isclose(after - before, harvest, abs_tol=1e-10),
                        "harvest_plus_reward": math.isclose(after - before, harvest + reward, abs_tol=1e-10),
                    }
                )
            elif kind == "combat":
                key = (time, int(event["attacker"]), int(event["victim"]))
                combats[key] += 1
                assert combats[key] <= attacks[key]
            elif kind == "death":
                aid = int(event["id"])
                assert aid in active and aid not in deaths
                combat = (
                    previous is not None
                    and previous["kind"] == "combat"
                    and int(previous["victim"]) == aid
                    and int(previous["time"]) == time
                )
                starved = float(event["sugar"]) <= 0 or (
                    event["spice_enabled"] == "True" and float(event["spice"]) <= 0
                )
                old = int(event["max_age_or_minus1"]) >= 0 and int(event["age"]) >= int(event["max_age_or_minus1"])
                assert combat or starved or old, ("unexplained natural death", event)
                deaths[aid] = {"time": time, "combat": combat, "starved": starved, "old": old}
                active.remove(aid)
            elif kind == "birth":
                aid = int(event["new_id"])
                parent = int(event["parent"])
                assert aid not in ever
                ever.add(aid)
                active.add(aid)
                assert parent in deaths and deaths[parent]["time"] == time and not deaths[parent]["combat"]
                assert parent not in births
                births[parent] = aid
            else:
                raise AssertionError(kind)
            previous = event
        assert active == agents[time + 1], ("trace/population mismatch", label, time)
    assert len(deaths) == totals["death"]
    assert sum(combats.values()) == sum(d["combat"] for d in deaths.values())
    replacement = any(
        line.startswith("R rule active (replace):") and line.endswith("True")
        for line in (args.root / "reference" / f"{label}.scenario.txt").read_text().splitlines()
    )
    assert set(births) == {aid for aid, d in deaths.items() if replacement and not d["combat"]}
    assert all(row["harvest_plus_reward"] for row in reward_rows), "Reward must reach stored wealth"
    results.append(
        {
            "case": label,
            "constructor": constructor,
            "steps": steps,
            "csv_hashes": hashes,
            "original_export_equality": equality,
            "initial_conditions_exact": True,
            "audited_agent_observations": sum(map(len, agents.values())),
            "events_sha256": hashlib.sha256(raw_events).hexdigest(),
            "event_counts": dict(totals),
            "final_population": len(active),
            "population_accounting_every_step_exact": True,
            "natural_starvation_only": sum(not d["combat"] and d["starved"] and not d["old"] for d in deaths.values()),
            "natural_age_only": sum(not d["combat"] and d["old"] and not d["starved"] for d in deaths.values()),
            "natural_both": sum(not d["combat"] and d["old"] and d["starved"] for d in deaths.values()),
            "replacement_births": len(births),
            "undelivered_attack_count": sum(attacks.values()) - sum(combats.values()),
            "attack_wealth_diagnostics": reward_rows,
        }
    )
report = {
    "source_files_verified": len(protocol["original"]["source_sha256"]),
    "changed_files": changed,
    "traced_binary_sha256": hashlib.sha256((args.root / "observe").read_bytes()).hexdigest(),
    "observer_unchanged": True,
    "cases": results,
    "scope": (
        "Three unchanged complete controls and two matched-initialization corrected combat trajectories. "
        "Event accounting verified at every step; no ensemble or whole-paper verdict."
    ),
}
with args.output.open("x") as stream:
    stream.write(json.dumps(report, indent=2, allow_nan=False) + "\n")
print(
    json.dumps(
        {
            r["case"]: {k: v for k, v in r.items() if k not in ["attack_wealth_diagnostics", "csv_hashes"]}
            for r in results
        }
    )
)
