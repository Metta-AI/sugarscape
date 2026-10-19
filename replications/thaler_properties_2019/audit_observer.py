"""Compare full native trajectories, preserving independent spatial discrepancies."""

import argparse
import csv
import hashlib
import json
import math
from pathlib import Path
import re

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("observed", type=Path)
parser.add_argument("ensembles", type=Path)
parser.add_argument("--output", type=Path, required=True)
args = parser.parse_args()
assets = Path(__file__).resolve().parent
observed = args.observed
pins = json.loads((assets / "source-manifest.json").read_text())["source_sha256"]
for name, digest in pins.items():
    assert (
        hashlib.sha256((observed / "source" / name).read_bytes()).hexdigest() == digest
    ), name
report = {"source_files_unchanged": len(pins), "cases": []}
for name, folder, horizon in [
    ("wealth", "wealth-first", 200),
    ("carrying", "carrying-ensemble", 400),
    ("trading", "trading-ensemble", 1000),
]:
    raw_path = args.ensembles / folder / "000-602352629/dynamics.m"
    raw = raw_path.read_text()
    original = {}
    original_trades = {}
    populations = {}
    for time, block in re.findall(r"^\{ (\d+),\n(.*?)^\}\n", raw, re.M | re.S):
        t = int(time)
        populations[t] = 0
        for line in block.splitlines():
            match = re.fullmatch(
                r"\[(\d+), ([^,]+), ([^,]+), ([^,]+), ([^,]+), ([^,]+), ([^,]+), \{\[([01,]*)\]\}, \{\[([^\]]*)\]\}\], ",
                line,
            )
            assert match, (name, "raw syntax", line)
            key = (t, int(match[1]))
            assert key not in original
            original[key] = [float(match[i]) for i in range(2, 8)] + [
                match[8].replace(",", "")
            ]
            values = (
                [float(v) for v in match[9].rstrip(",").split(",")] if match[9] else []
            )
            original_trades[key] = [
                tuple(values[i : i + 3]) for i in range(0, len(values), 3)
            ]
            populations[t] += 1
    agents = list(csv.DictReader((observed / f"{name}.agents.csv").open()))
    by_time = {t: [] for t in range(horizon + 1)}
    shared = {}
    for row in agents:
        t = int(row["time"])
        by_time[t].append(row)
        if t:
            key = (t, int(row["id"]))
            assert key not in shared
            shared[key] = [
                float(row[k])
                for k in [
                    "age",
                    "sugar",
                    "spice",
                    "sugar_metabolism",
                    "vision",
                    "gender",
                ]
            ] + [row["culture"]]
    assert shared == original, (name, "shared agent measurements differ")
    trades = {key: [] for key in original}
    for row in csv.DictReader((observed / f"{name}.trades.csv").open()):
        if int(row["time"]):
            trades[(int(row["time"]), int(row["id"]))].append(
                tuple(float(row[k]) for k in ["price", "sugar", "spice"])
            )
    assert trades == original_trades, (name, "shared trades differ")
    summaries = list(csv.DictReader((observed / f"{name}.summary.csv").open()))
    assert [int(row["time"]) for row in summaries] == list(range(horizon + 1)), (
        name,
        "timestamps",
    )
    for row in summaries:
        t = int(row["time"])
        assert int(row["population"]) == len(by_time[t]), (name, t, "population")
        for field in ["sugar", "spice"]:
            assert math.isclose(
                float(row["agent_" + field]),
                sum(float(a[field]) for a in by_time[t]),
                rel_tol=1e-12,
                abs_tol=1e-9,
            ), (name, t, field)
        assert int(row["infected"]) == sum(
            int(a["disease_count"]) > 0 for a in by_time[t]
        ), (name, t, "infected")
    cells = list(csv.DictReader((observed / f"{name}.cells.csv").open()))
    spatial = []
    for t in [0, horizon]:
        rows = [row for row in cells if int(row["time"]) == t]
        coords = {(int(r["x"]), int(r["y"])) for r in rows}
        owners = {
            int(r["occupier"]): (int(r["x"]), int(r["y"]))
            for r in rows
            if int(r["occupier"]) >= 0
        }
        positions = {int(r["id"]): (int(r["x"]), int(r["y"])) for r in by_time[t]}
        assert len(positions) == len(by_time[t]), (name, t, "duplicate agents")
        assert len(coords) == len(rows), (name, t, "duplicate cell coordinates")
        for r in rows:
            assert 0 <= float(r["sugar"]) <= float(r["sugar_capacity"]) <= 4, (
                name,
                t,
                "sugar bounds",
            )
            assert 0 <= float(r["spice"]) <= float(r["spice_capacity"]) <= 4, (
                name,
                t,
                "spice bounds",
            )
            assert float(r["pollution"]) >= 0, (name, t, "pollution bounds")
        spatial.append(
            {
                "time": t,
                "cells": len(rows),
                "nominal_cells": 2601,
                "occupiers": len(owners),
                "agents": len(positions),
                "coordinate_disagreements": sum(
                    owners.get(aid) != pos for aid, pos in positions.items()
                ),
                "unoccupied_agent_ids": sorted(set(positions) - set(owners)),
                "declared_dimensions": [51, 51],
                "index_formula": "50*y+x",
                "distinct_nominal_indices": len(
                    {50 * y + x for y in range(51) for x in range(51)}
                ),
            }
        )
    report["cases"].append(
        {
            "scenario": name,
            "horizon": horizon,
            "matching_agent_observations": len(shared),
            "matching_trade_observations": sum(map(len, trades.values())),
            "raw_sha256": hashlib.sha256(raw_path.read_bytes()).hexdigest(),
            "observer_sha256": {
                p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                for p in sorted(observed.glob(name + ".*"))
            },
            "spatial_discrepancies": spatial,
        }
    )
report["interpretation"] = (
    "Shared measurements match exactly. Spatial invariants fail in the unchanged model: coordToIdx uses width-1, aliasing 50 pairs on its declared 51x51 grid. Agent.hs additionally constructs observables from pre-event s rather than updated s-prime; same-time occupancy agreement is not a valid invariant for those observations. No corrected-model or paper-negative verdict."
)
output = args.output
assert not output.exists()
output.write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps(report, indent=2))
