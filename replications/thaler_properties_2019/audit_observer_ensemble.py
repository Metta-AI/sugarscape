"""Independently audit full native appendix trajectories and source/prose predicates."""

import argparse
import csv
import gzip
import hashlib
import json
import math
from pathlib import Path

import numpy as np
from scipy import stats

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("run", type=Path)
parser.add_argument("protocol", type=Path)
parser.add_argument(
    "scenario", choices=["terracing", "disease_clear", "disease_persist", "culture"]
)
parser.add_argument("output", type=Path)
parser.add_argument("--allow-prefix", action="store_true")
parser.add_argument(
    "--interval", nargs=2, type=int, default=[0, 100], metavar=("START", "STOP")
)
args = parser.parse_args()
protocol = json.loads(args.protocol.read_text())
manifest = json.loads((args.run / "manifest.json").read_text())
assert manifest["protocol"] == protocol
variant = manifest["variant"]
assert variant in protocol["variants"]
assert (
    hashlib.sha256((args.run / "run_observer_ensemble.py").read_bytes()).hexdigest()
    == manifest["runner_sha256"]
)
ledger = (args.run / "completed.jsonl").read_bytes()
assert ledger.endswith(b"\n")
all_records = [json.loads(line) for line in ledger.splitlines()]
start, stop = args.interval
assert 0 <= start < stop <= 100
if args.interval != [0, 100]:
    assert manifest["interval"] == args.interval
expected_order = [
    (s["key"], i) for s in protocol["scenarios"] for i in range(start, stop)
]
assert [(r["scenario"], r["index"]) for r in all_records] == expected_order[
    : len(all_records)
]
records = [r for r in all_records if r["scenario"] == args.scenario]
assert 0 < len(records) <= stop - start
assert args.allow_prefix or len(records) == stop - start, (
    "Every seed in the declared interval is required"
)
scenario = next(s for s in protocol["scenarios"] if s["key"] == args.scenario)
horizon = scenario["steps"]
stride = scenario["stride"]
frames = sorted(set(range(0, horizon + 1, stride)) | {horizon})
summary_fields = [
    "time",
    "population",
    "infected",
    "zero_dominant",
    "red",
    "blue",
    "agent_sugar",
    "agent_spice",
    "trade_count",
    "price_sum",
    "price_sum_squares",
    "environment_sugar",
    "environment_spice",
    "pollution",
]
results = []
for record in records:
    index, seed = record["index"], record["seed"]
    assert seed == protocol["seeds"][index] and record["variant"] == variant
    folder = args.run / args.scenario / f"{index:03d}-{seed}"
    expected_files = {
        "command.json",
        "exit.json",
        "stdout.log",
        "stderr.log",
        "trajectory.scenario.txt",
    } | {
        f"trajectory.{kind}.csv{suffix}"
        for kind in ["summary", "agents", "trades", "cells"]
        for suffix in ["", ".gz"]
    }
    assert set(record["files_sha256"]) == expected_files
    for name, digest in record["files_sha256"].items():
        assert hashlib.sha256((folder / name).read_bytes()).hexdigest() == digest, (
            index,
            name,
        )
    for kind in ["summary", "agents", "trades", "cells"]:
        assert (
            gzip.decompress((folder / f"trajectory.{kind}.csv.gz").read_bytes())
            == (folder / f"trajectory.{kind}.csv").read_bytes()
        )
    command = json.loads((folder / "command.json").read_text())
    assert command[:5] == [
        protocol["variants"][variant]["root"] + "/observe",
        scenario["constructor"],
        str(seed),
        str(horizon),
        str(stride),
    ]
    expected_parent = Path(command[5]).parent
    assert (
        expected_parent.name == folder.name
        and expected_parent.parent.name == args.scenario
        and expected_parent.parent.parent.name == variant
    )
    assert Path(command[5]).name == "trajectory"
    assert (
        (folder / "trajectory.scenario.txt")
        .read_text()
        .startswith(f"Constructor: {scenario['constructor']}\nSeed: {seed}\n")
    )
    assert json.loads((folder / "exit.json").read_text()) == {"exit_code": 0}
    summaries = list(csv.DictReader((folder / "trajectory.summary.csv").open()))
    assert list(summaries[0]) == summary_fields
    assert [int(r["time"]) for r in summaries] == list(range(horizon + 1))
    assert len(summaries) == record["summary_rows"] and record["steps"] == horizon
    assert int(summaries[-1]["population"]) == record["final_population"]
    for r in summaries:
        assert all(math.isfinite(float(value)) for value in r.values())
        population = int(r["population"])
        assert 0 <= int(r["infected"]) <= population
        assert 0 <= int(r["zero_dominant"]) <= population
        assert int(r["red"]) + int(r["blue"]) == population
        assert (
            int(r["trade_count"]) == 0
            and float(r["price_sum"]) == float(r["price_sum_squares"]) == 0
        )
    agents = {t: {} for t in frames}
    for r in csv.DictReader((folder / "trajectory.agents.csv").open()):
        t, aid = int(r["time"]), int(r["id"])
        assert t in agents and aid not in agents[t]
        assert all(
            math.isfinite(float(value)) for key, value in r.items() if key != "culture"
        )
        assert set(r["culture"]) <= {"0", "1"}
        assert len(r["culture"]) == (10 if args.scenario == "culture" else 0)
        assert int(r["disease_count"]) >= 0
        assert 0 <= int(r["x"]) < 51 and 0 <= int(r["y"]) < 51
        agents[t][aid] = r
    assert list(csv.DictReader((folder / "trajectory.trades.csv").open())) == []
    for t, members in agents.items():
        row = summaries[t]
        assert len(members) == int(row["population"])
        assert sum(int(a["disease_count"]) > 0 for a in members.values()) == int(
            row["infected"]
        )
        assert sum(
            2 * a["culture"].count("0") > len(a["culture"]) for a in members.values()
        ) == int(row["zero_dominant"])
        assert sum(int(a["tribe"]) == 1 for a in members.values()) == int(row["red"])
        assert sum(int(a["tribe"]) == 0 for a in members.values()) == int(row["blue"])
        for field in ["sugar", "spice"]:
            assert math.isclose(
                sum(float(a[field]) for a in members.values()),
                float(row["agent_" + field]),
                rel_tol=1e-12,
                abs_tol=1e-9,
            )
    sites = {0: {}, horizon: {}}
    width = {
        "original": 50,
        "corrected": 51,
        "disease_count_corrected": 50,
        "combined_corrected": 51,
    }[variant]
    for r in csv.DictReader((folder / "trajectory.cells.csv").open()):
        t, x, y = int(r["time"]), int(r["x"]), int(r["y"])
        assert t in sites and 0 <= x < 51 and 0 <= y < 51
        key = width * y + x
        assert key not in sites[t]
        assert all(math.isfinite(float(v)) for v in r.values())
        assert 0 <= float(r["sugar"]) <= float(r["sugar_capacity"]) <= 4
        assert 0 <= float(r["spice"]) <= float(r["spice_capacity"]) <= 4
        assert float(r["pollution"]) >= 0
        sites[t][key] = r
    spatial = []
    for t, cells in sites.items():
        assert set(cells) == set(range(50 * width + 51))
        for field in ["sugar", "spice", "pollution"]:
            summary_field = field if field == "pollution" else "environment_" + field
            assert math.isclose(
                sum(float(c[field]) for c in cells.values()),
                float(summaries[t][summary_field]),
                rel_tol=1e-12,
                abs_tol=1e-9,
            )
        occupied = [r for r in cells.values() if int(r["occupier"]) >= 0]
        owners = {int(r["occupier"]): (int(r["x"]), int(r["y"])) for r in occupied}
        positions = {aid: (int(r["x"]), int(r["y"])) for aid, r in agents[t].items()}
        spatial.append(
            {
                "time": t,
                "cells": len(cells),
                "agents": len(positions),
                "occupiers": len(occupied),
                "duplicate_occupier_ids": len(occupied) - len(owners),
                "missing_occupier_ids": sorted(set(positions) - set(owners)),
                "coordinate_disagreements": sum(
                    aid not in owners or owners[aid] != xy
                    for aid, xy in positions.items()
                ),
            }
        )
    final_population = int(summaries[-1]["population"])
    row = {
        "index": index,
        "seed": seed,
        "steps": horizon,
        "summary_observations": len(summaries),
        "snapshot_agent_observations": sum(len(a) for a in agents.values()),
        "final_population": final_population,
        "final_infected": int(summaries[-1]["infected"]),
        "extinct": final_population == 0,
        "spatial": spatial,
        "source_record_sha256": hashlib.sha256(
            json.dumps(record, sort_keys=True).encode()
        ).hexdigest(),
    }
    if args.scenario == "terracing":
        assert final_population > 0
        uniform, edge = 0, 0
        for agent in agents[horizon].values():
            x, y = int(agent["x"]), int(agent["y"])
            level = float(sites[horizon][width * y + x]["sugar"])
            neighbors = [
                float(sites[horizon][width * ((y + dy) % 51) + (x + dx) % 51]["sugar"])
                for dx, dy in [(0, -1), (-1, 0), (1, 0), (0, 1)]
            ]
            uniform += all(value == level for value in neighbors)
            edge += any(value < level for value in neighbors)
        stability = {}
        for baseline_time in [50, 51]:
            baseline = agents[baseline_time]
            values = []
            for t in range(baseline_time + 1, horizon + 1):
                assert agents[t] and set(agents[t]) <= set(baseline)
                same = sum(
                    (r["x"], r["y"]) == (baseline[aid]["x"], baseline[aid]["y"])
                    for aid, r in agents[t].items()
                )
                values.append(same / len(agents[t]))
            stability[str(baseline_time)] = float(np.mean(values))
        row["measurements"] = {
            "source_terracing_ratio": uniform / final_population,
            "prose_edge_ratio": edge / final_population,
            "source_stability_ratio": stability["51"],
            "prose_stability_ratio": stability["50"],
        }
    elif args.scenario == "disease_clear":
        cleared = [
            int(r["time"])
            for r in summaries[1:100]
            if int(r["infected"]) == 0 and int(r["population"]) > 0
        ]
        row["first_clear_before100"] = cleared[0] if cleared else None
        row["predicates"] = {
            "source_zero_infected_at100": row["final_infected"] == 0,
            "prose_clear_before100_with_survivors": bool(cleared),
        }
    elif args.scenario == "disease_persist":
        row["predicates"] = {
            "source_above_ceil_half": row["final_infected"]
            > math.ceil(final_population / 2),
            "prose_strict_majority": 2 * row["final_infected"] > final_population,
        }
    else:
        if final_population:
            ratio = int(summaries[-1]["zero_dominant"]) / final_population
            row["zero_dominant_ratio"] = ratio
            row["predicates"] = {
                "source_culture_predicate": ratio >= 0.95
                or ratio <= (1 - 0.95)
                or ratio >= 0.45
                or (1 - ratio) <= 0.45,
                "prose_symmetric_global_ratio": ratio >= 0.95
                or ratio <= (1 - 0.95)
                or 0.45 <= ratio <= 0.55,
            }
        else:
            row["status"] = "undefined_cultural_ratio_extinction"
            row["predicates"] = {}
    results.append(row)
comparisons = []
complete = len(results) == 100
if complete and args.scenario == "terracing":
    for metric, target in [
        ("source_terracing_ratio", 0.45),
        ("source_stability_ratio", 0.95),
        ("prose_edge_ratio", 0.45),
        ("prose_stability_ratio", 0.95),
    ]:
        values = np.array([r["measurements"][metric] for r in results])
        mean = float(values.mean())
        sem = float(stats.sem(values))
        margin = float(stats.t.ppf(0.975, 99) * sem)
        comparisons.append(
            {
                "metric": metric,
                "n": 100,
                "mean": mean,
                "standard_error": sem,
                "zero_variance": sem == 0,
                "ci95": [mean - margin, mean + margin],
                "target": target,
                "target_inside_ci": mean - margin <= target <= mean + margin,
            }
        )
        if metric.startswith("source_"):
            if sem == 0:
                comparisons[-1]["source_statistical_rule"] = {
                    "status": "undefined_zero_variance",
                    "caller_default_pass": True,
                }
            else:
                p_value = float(2 * stats.t.sf(abs((mean - target) / sem), 99))
                comparisons[-1]["source_statistical_rule"] = {
                    "status": "defined_on_frozen100seed_sample",
                    "p_value": p_value,
                    "accepts_null": p_value > 0.05,
                }
if complete and args.scenario != "terracing" and all(r["predicates"] for r in results):
    for predicate in results[0]["predicates"]:
        passes = sum(r["predicates"][predicate] for r in results)
        lower = float(stats.beta.ppf(0.025, passes, 101 - passes)) if passes else 0.0
        upper = (
            float(stats.beta.ppf(0.975, passes + 1, 100 - passes))
            if passes < 100
            else 1.0
        )
        comparisons.append(
            {
                "predicate": predicate,
                "passes": passes,
                "n": 100,
                "exact_binomial_ci95": [lower, upper],
            }
        )
report = {
    "variant": variant,
    "scenario": args.scenario,
    "validated_runs": len(results),
    "complete_scenario": complete,
    "summary_observations": sum(r["summary_observations"] for r in results),
    "snapshot_agent_observations": sum(
        r["snapshot_agent_observations"] for r in results
    ),
    "extinction_count": sum(r["extinct"] for r in results),
    "protocol_sha256": hashlib.sha256(args.protocol.read_bytes()).hexdigest(),
    "manifest_sha256": hashlib.sha256(
        (args.run / "manifest.json").read_bytes()
    ).hexdigest(),
    "ledger_snapshot_sha256": hashlib.sha256(ledger).hexdigest(),
    "results": results,
    "comparisons": comparisons,
    "scope": (
        "Source and prose predicates measured separately. Corrected variant is post-hoc sensitivity. "
        "No full-paper credit; global culture ratio does not prove spatial hill dominance."
    ),
}
args.output.mkdir(parents=True, exist_ok=False)
(args.output / "ledger-snapshot.jsonl").write_bytes(ledger)
(args.output / "audit.json").write_text(
    json.dumps(report, indent=2, allow_nan=False) + "\n"
)
print(json.dumps({k: v for k, v in report.items() if k != "results"}))
