"""Audit the complete first native book-parameter spice trajectory."""

import argparse
import csv
import gzip
import hashlib
import json
import math
from pathlib import Path

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("root", type=Path)
parser.add_argument("protocol", type=Path)
parser.add_argument("output", type=Path)
parser.add_argument("native", type=Path)
parser.add_argument("control", type=Path)
args = parser.parse_args()
root = args.root
protocol = json.loads(args.protocol.read_text())
v = protocol["variants"]["original"]
for name, digest in v["source_sha256"].items():
    assert hashlib.sha256((args.native / "source" / name).read_bytes()).hexdigest() == digest
assert hashlib.sha256((args.native / "observe").read_bytes()).hexdigest() == v["binary_sha256"]
assert hashlib.sha256((args.native / "Observe.hs").read_bytes()).hexdigest() == v["observer_sha256"]
manifest = json.loads((root / "manifest.json").read_text())
assert manifest["protocol"] == protocol and manifest["interval"] == [0, 1]
assert json.loads((root / "complete.json").read_text()) == {"completed_runs": 1}
assert hashlib.sha256((root / "run_observer_ensemble.py").read_bytes()).hexdigest() == manifest["runner_sha256"]
records = [json.loads(line) for line in (root / "completed.jsonl").read_text().splitlines()]
assert [r["scenario"] for r in records] == ["spice_book"]
initial = {}
cases = []
texts = []
for record, scenario in zip(records, protocol["scenarios"], strict=True):
    assert record["index"] == 0 and record["seed"] == protocol["seeds"][0] and record["steps"] == 1000
    folder = root / record["scenario"] / f"000-{record['seed']}"
    for name, digest in record["files_sha256"].items():
        assert hashlib.sha256((folder / name).read_bytes()).hexdigest() == digest
    for kind in ["summary", "agents", "trades", "cells"]:
        assert (
            gzip.decompress((folder / f"trajectory.{kind}.csv.gz").read_bytes())
            == (folder / f"trajectory.{kind}.csv").read_bytes()
        )
    command = json.loads((folder / "command.json").read_text())
    assert command[:5] == [
        protocol["variants"]["original"]["root"] + "/observe",
        scenario["constructor"],
        str(record["seed"]),
        "1000",
        "10",
    ]
    summaries = list(csv.DictReader((folder / "trajectory.summary.csv").open()))
    assert [int(r["time"]) for r in summaries] == list(range(1001))
    assert all(math.isfinite(float(v)) for r in summaries for v in r.values())
    agents = {t: [] for t in range(0, 1001, 10)}
    for r in csv.DictReader((folder / "trajectory.agents.csv").open()):
        agents[int(r["time"])].append(r)
        assert all(math.isfinite(float(v)) for k, v in r.items() if k != "culture")
    trades = {t: [] for t in agents}
    for r in csv.DictReader((folder / "trajectory.trades.csv").open()):
        trades[int(r["time"])].append(r)
        assert all(math.isfinite(float(v)) for v in r.values())
    for t, group in agents.items():
        assert len(group) == int(summaries[t]["population"]) == len({r["id"] for r in group})
        assert len(trades[t]) == int(summaries[t]["trade_count"])
        for field in ["sugar", "spice"]:
            assert math.isclose(
                sum(float(r[field]) for r in group),
                float(summaries[t]["agent_" + field]),
                rel_tol=1e-12,
                abs_tol=1e-9,
            )
    cells = list(csv.DictReader((folder / "trajectory.cells.csv").open()))
    initial[record["scenario"]] = {
        "agents": agents[0],
        "cells": [r for r in cells if r["time"] == "0"],
        "summary": summaries[0],
    }
    texts.append((folder / "trajectory.scenario.txt").read_text().splitlines())
    cases.append(
        {
            "scenario": record["scenario"],
            "horizon": 1000,
            "snapshot_agent_observations": sum(map(len, agents.values())),
            "snapshot_trade_records": sum(map(len, trades.values())),
            "final_population": int(summaries[-1]["population"]),
        }
    )
control = args.control.read_text().splitlines()
book = texts[0]
assert len(control) == len(book)
differences = [{"control": a, "book": b} for a, b in zip(control, book, strict=True) if a != b]
labels = ["Constructor:", "Scenario:", "Vision range:", "Sugar metabolism range:", "Spice metabolism range:"]
assert len(differences) == len(labels)
for row, label in zip(differences, labels, strict=True):
    assert row["control"].startswith(label) and row["book"].startswith(label)
assert differences[2]["control"].endswith("(1,6)") and differences[2]["book"].endswith("(1,10)")
for row in differences[3:]:
    assert row["control"].endswith("(1,4)") and row["book"].endswith("(1,5)")
population = [int(row["population"]) for row in summaries]
assert population[0] == 400
below = [t for t, pop in enumerate(population) if pop < 90]
report = {
    "cases": cases,
    "source_files_verified": len(v["source_sha256"]),
    "resolved_control_differences": differences,
    "control_scenario_sha256": hashlib.sha256(args.control.read_bytes()).hexdigest(),
    "population_at_0_100_500_1000": {str(t): population[t] for t in [0, 100, 500, 1000]},
    "first_below_90": below[0] if below else None,
    "population_trajectory": population,
    "scope": (
        "One original-source trajectory; comparison differs only in documented vision and metabolism ranges. "
        "No ensemble or full-paper claim."
    ),
}
with args.output.open("x") as stream:
    stream.write(json.dumps(report, indent=2, allow_nan=False) + "\n")
print(json.dumps({k: v for k, v in report.items() if k != "population_trajectory"}))
