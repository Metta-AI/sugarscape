"""Audit native combat trajectories, retained first seeds, and paired reward correction."""

import argparse
import csv
import gzip
import hashlib
import json
import math
from collections import Counter
from pathlib import Path

import numpy as np
from scipy.stats import t as student_t


def audit_events(
    prefix, events_path, label, constructor, steps, stride, variant, protocol
):
    summaries = list(csv.DictReader(Path(str(prefix) + ".summary.csv").open()))
    assert [int(r["time"]) for r in summaries] == list(range(steps + 1))
    assert all(math.isfinite(float(v)) for row in summaries for v in row.values())
    agents = {t: set() for t in range(0, steps + 1, stride)}
    for row in csv.DictReader(Path(str(prefix) + ".agents.csv").open()):
        assert all(math.isfinite(float(v)) for k, v in row.items() if k != "culture")
        t = int(row["time"])
        aid = int(row["id"])
        assert aid not in agents[t]
        agents[t].add(aid)
    assert all(len(ids) == int(summaries[t]["population"]) for t, ids in agents.items())
    raw_events = events_path.read_bytes()
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
                        "harvest_only": math.isclose(
                            after - before, harvest, abs_tol=1e-10
                        ),
                        "harvest_plus_reward": math.isclose(
                            after - before, harvest + reward, abs_tol=1e-10
                        ),
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
                old = int(event["max_age_or_minus1"]) >= 0 and int(event["age"]) >= int(
                    event["max_age_or_minus1"]
                )
                assert combat or starved or old, ("unexplained natural death", event)
                deaths[aid] = {
                    "time": time,
                    "combat": combat,
                    "starved": starved,
                    "old": old,
                }
                active.remove(aid)
            elif kind == "birth":
                aid = int(event["new_id"])
                parent = int(event["parent"])
                assert aid not in ever
                ever.add(aid)
                active.add(aid)
                assert (
                    parent in deaths
                    and deaths[parent]["time"] == time
                    and not deaths[parent]["combat"]
                )
                assert parent not in births
                births[parent] = aid
            else:
                raise AssertionError(kind)
            previous = event
        assert len(active) == int(summaries[time + 1]["population"]), (label, time)
        if time + 1 in agents:
            assert active == agents[time + 1], ("trace/IDs mismatch", label, time)
    assert len(deaths) == totals["death"]
    assert sum(combats.values()) == sum(d["combat"] for d in deaths.values())
    replacement = any(
        line.startswith("R rule active (replace):") and line.endswith("True")
        for line in Path(str(prefix) + ".scenario.txt").read_text().splitlines()
    )
    assert set(births) == {
        aid for aid, d in deaths.items() if replacement and not d["combat"]
    }
    expected_credit = (
        "harvest_plus_reward" if variant == "reward_corrected" else "harvest_only"
    )
    assert all(row[expected_credit] for row in reward_rows), (
        variant,
        "unexpected reward accounting",
    )
    killers = Counter()
    for (_, attacker, _), count in combats.items():
        killers[attacker] += count
    return {
        "case": label,
        "constructor": constructor,
        "steps": steps,
        "initial_conditions_exact": True,
        "audited_agent_observations": sum(map(len, agents.values())),
        "events_sha256": hashlib.sha256(raw_events).hexdigest(),
        "event_counts": dict(totals),
        "combat_kills": sum(combats.values()),
        "final_population": len(active),
        "population_accounting_every_step_exact": True,
        "natural_starvation_only": sum(
            not d["combat"] and d["starved"] and not d["old"] for d in deaths.values()
        ),
        "natural_age_only": sum(
            not d["combat"] and d["old"] and not d["starved"] for d in deaths.values()
        ),
        "natural_both": sum(
            not d["combat"] and d["old"] and d["starved"] for d in deaths.values()
        ),
        "replacement_births": len(births),
        "undelivered_attack_count": sum(attacks.values()) - sum(combats.values()),
        "attacks_with_positive_reward": sum(r["reward"] > 0 for r in reward_rows),
        "computed_reward_sum": sum(r["reward"] for r in reward_rows),
        "reward_accounting_exact": True,
        "kills_by_attacker": dict(sorted(killers.items())),
        "largest_individual_kill_count": max(killers.values(), default=0),
        "first_single_agent_time": next(
            (int(r["time"]) for r in summaries if int(r["population"]) == 1), None
        ),
        "population_trajectory": [int(r["population"]) for r in summaries],
    }


parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("protocol", type=Path)
parser.add_argument(
    "native_home", type=Path, help="Host directory corresponding to /root/sugarscape"
)
parser.add_argument("runs", type=Path)
parser.add_argument("output", type=Path)
parser.add_argument("--allow-prefix", action="store_true")
args = parser.parse_args()
protocol = json.loads(args.protocol.read_text())
assert (
    protocol["replications"]
    == len(protocol["seeds"])
    == len(set(protocol["seeds"]))
    == 100
)
assert not args.output.exists()
variants = ["instrumented_original", "reward_corrected"]
assert list(protocol["variants"]) == variants
ledgers = {}
records = {}
for variant in variants:
    root = args.runs / variant
    manifest = json.loads((root / "manifest.json").read_text())
    assert manifest["protocol"] == protocol and manifest["variant"] == variant
    assert manifest["interval"] == [1, 100]
    assert (
        hashlib.sha256((root / "run_observer_ensemble.py").read_bytes()).hexdigest()
        == manifest["runner_sha256"]
    )
    raw = (root / "completed.jsonl").read_bytes()
    assert raw.endswith(b"\n"), "Retry after the worker finishes its ledger append"
    ledgers[variant] = raw
    records[variant] = {}
    for line in raw.splitlines():
        record = json.loads(line)
        key = (record["scenario"], record["index"])
        assert key not in records[variant] and record["variant"] == variant
        assert 1 <= record["index"] < 100
        assert record["seed"] == protocol["seeds"][record["index"]]
        assert record["scenario"] in [s["key"] for s in protocol["scenarios"]]
        records[variant][key] = record
paired = {}
for scenario in protocol["scenarios"]:
    label = scenario["key"]
    sets = [
        {0} | {index for name, index in records[v] if name == label} for v in variants
    ]
    paired[label] = sorted(sets[0] & sets[1])
    if not args.allow_prefix:
        assert sets == [set(range(100)), set(range(100))], (
            label,
            "Full 100 pairs required",
            list(map(len, sets)),
        )

for variant in variants:
    specification = protocol["variants"][variant]
    native = args.native_home / Path(specification["root"]).relative_to(
        "/root/sugarscape"
    )
    for name, digest in specification["source_sha256"].items():
        assert (
            hashlib.sha256((native / "source" / name).read_bytes()).hexdigest()
            == digest
        )
    for name, key in [("observe", "binary_sha256"), ("Observe.hs", "observer_sha256")]:
        assert (
            hashlib.sha256((native / name).read_bytes()).hexdigest()
            == specification[key]
        )
    retained = protocol["retained_first_seed"][variant]
    assert retained["index"] == 0 and retained["seed"] == protocol["seeds"][0]
    assert retained["steps"] == 1000 and retained["stride"] == 1
    first = args.native_home / Path(retained["root"]).relative_to("/root/sugarscape")
    for name, digest in retained["files_sha256"].items():
        assert hashlib.sha256((first / name).read_bytes()).hexdigest() == digest

results = []
for scenario in protocol["scenarios"]:
    label, constructor, steps = (
        scenario["key"],
        scenario["constructor"],
        scenario["steps"],
    )
    for index in paired[label]:
        initial = []
        for variant in variants:
            if index == 0:
                retained = protocol["retained_first_seed"][variant]
                root = args.native_home / Path(retained["root"]).relative_to(
                    "/root/sugarscape"
                )
                prefix = root / label
                events_path = root / f"{label}.stderr.log"
                stride = retained["stride"]
            else:
                record = records[variant][label, index]
                root = (
                    args.runs
                    / variant
                    / label
                    / f"{index:03d}-{protocol['seeds'][index]}"
                )
                required = {
                    "command.json",
                    "exit.json",
                    "stderr.log",
                    "stdout.log",
                    "trajectory.scenario.txt",
                }
                required.update(
                    f"trajectory.{kind}.csv{extension}"
                    for kind in ["agents", "summary", "cells", "trades"]
                    for extension in ["", ".gz"]
                )
                assert set(record["files_sha256"]) == required
                for name, digest in record["files_sha256"].items():
                    assert (
                        hashlib.sha256((root / name).read_bytes()).hexdigest() == digest
                    ), (root, name)
                for path in root.glob("*.csv.gz"):
                    assert (
                        gzip.decompress(path.read_bytes())
                        == path.with_suffix("").read_bytes()
                    )
                assert json.loads((root / "exit.json").read_text()) == {"exit_code": 0}
                command = json.loads((root / "command.json").read_text())
                stride = scenario["stride"]
                assert command[:5] == [
                    protocol["variants"][variant]["root"] + "/observe",
                    constructor,
                    str(protocol["seeds"][index]),
                    str(steps),
                    str(stride),
                ]
                assert Path(command[5]).parts[-4:] == (
                    variant,
                    label,
                    root.name,
                    "trajectory",
                )
                prefix = root / "trajectory"
                events_path = root / "stderr.log"
                assert record["steps"] == steps and record["summary_rows"] == steps + 1
            result = audit_events(
                prefix,
                events_path,
                label,
                constructor,
                steps,
                stride,
                variant,
                protocol,
            )
            result.update(
                variant=variant,
                index=index,
                seed=protocol["seeds"][index],
                stride=stride,
            )
            if index:
                assert result["final_population"] == record["final_population"]
            results.append(result)
            frames = {}
            for suffix in ["summary", "agents", "cells", "trades"]:
                with Path(str(prefix) + f".{suffix}.csv").open() as stream:
                    frames[suffix] = [
                        row for row in csv.DictReader(stream) if row["time"] == "0"
                    ]
            frames["scenario"] = Path(str(prefix) + ".scenario.txt").read_text()
            initial.append(frames)
        assert initial[0] == initial[1], (label, index, "initial conditions differ")

comparisons = []
if not args.allow_prefix:
    for scenario in protocol["scenarios"]:
        label = scenario["key"]
        for metric in [
            "final_population",
            "combat_kills",
            "natural_starvation_only",
            "natural_age_only",
            "natural_both",
            "replacement_births",
            "largest_individual_kill_count",
        ]:
            values = [
                [r[metric] for r in results if r["case"] == label and r["variant"] == v]
                for v in variants
            ]
            difference = np.asarray(values[1], dtype=float) - np.asarray(
                values[0], dtype=float
            )
            assert len(difference) == 100
            mean = float(difference.mean())
            half = float(
                student_t.ppf(0.975, 99) * difference.std(ddof=1) / math.sqrt(100)
            )
            comparisons.append(
                {
                    "scenario": label,
                    "metric": metric,
                    "pairs": 100,
                    "corrected_minus_original_mean": mean,
                    "paired_mean_ci95": [mean - half, mean + half],
                }
            )
sidecars = args.output.with_name(args.output.stem + "-ledgers")
sidecars.mkdir(exist_ok=False)
for variant, raw in ledgers.items():
    (sidecars / f"{variant}.jsonl").write_bytes(raw)
report = {
    "protocol_sha256": hashlib.sha256(args.protocol.read_bytes()).hexdigest(),
    "auditor_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    "ledger_sha256": {v: hashlib.sha256(raw).hexdigest() for v, raw in ledgers.items()},
    "paired_indices": paired,
    "unpaired_indices_not_audited": {
        v: {
            s["key"]: sorted(
                i
                for name, i in records[v]
                if name == s["key"] and i not in paired[name]
            )
            for s in protocol["scenarios"]
        }
        for v in variants
    },
    "prefix_only": args.allow_prefix,
    "results": results,
    "comparisons": comparisons,
    "scope": "1000-step diagnostics; no eventual convergence, spatial invasion, or whole-paper verdict. Grid aliasing and stale observations retained to isolate reward correction.",
}
with args.output.open("x") as stream:
    stream.write(json.dumps(report, indent=2, allow_nan=False) + "\n")
print(
    json.dumps(
        {
            "audited_runs": len(results),
            "paired_counts": {k: len(v) for k, v in paired.items()},
            "agent_observations": sum(r["audited_agent_observations"] for r in results),
            "comparisons": comparisons,
        }
    )
)
