"""Measure first-step death exposure in complete native initializer controls.

An available neighboring resource is an opportunity, not a predicted rescue:
movement-first conflict winners and later trajectories are not reconstructed.
"""

import argparse
import csv
import hashlib
import itertools
import json
from pathlib import Path

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("native", type=Path)
parser.add_argument("output", type=Path)
args = parser.parse_args()
assert not args.output.exists()
protocol = json.loads((args.native / "protocol.json").read_text())
records = []
for variant in protocol["variants"]:
    name = variant["variant"]
    source_path = args.native / "variants" / name / "src/main.cu"
    source = source_path.read_text()
    assert (
        hashlib.sha256(source_path.read_bytes()).hexdigest() == variant["source_sha256"]
    )
    metabolism_layer = "layer.addAgentFunction(metabolise_and_growback);"
    movement_layer = "layer.addSubModel(movement_sub);"
    assert source.count(metabolism_layer) == source.count(movement_layer) == 1
    assert source.index(metabolism_layer) < source.index(movement_layer)
    initial = args.native / "runs" / name / "initial-cells.csv"
    states = args.native / "runs" / name / "state.csv"
    with initial.open() as stream:
        cells = [{k: int(v) for k, v in r.items()} for r in csv.DictReader(stream)]
    assert len(cells) == 65536
    by_position = {(r["x"], r["y"]): r for r in cells}
    assert len(by_position) == 65536
    active = {r["id"]: r for r in cells if r["status"] == 1}
    with states.open() as stream:
        groups = itertools.groupby(csv.DictReader(stream), key=lambda r: int(r["step"]))
        step, rows = next(groups)
        assert step == -1
        assert {int(r["id"]) for r in rows} == active.keys()
        step, rows = next(groups)
        assert step == 0
        survivors = {int(r["id"]) for r in rows}
    dead = {
        identifier
        for identifier, r in active.items()
        if r["sugar"] + r["cell_sugar"] - r["metabolism"] <= 0
    }
    assert dead == active.keys() - survivors
    opportunities = []
    for identifier in sorted(dead):
        r = active[identifier]
        candidates = []
        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            target = by_position[((r["x"] + dx) % 256, (r["y"] + dy) % 256)]
            if (
                target["status"] == 0
                and target["cell_sugar"] > r["cell_sugar"]
                and r["sugar"] + target["cell_sugar"] - r["metabolism"] > 0
            ):
                candidates.append({k: target[k] for k in ["x", "y", "cell_sugar"]})
        if candidates:
            opportunities.append(
                {"agent": r, "initial_empty_cardinal_candidates": candidates}
            )
    records.append(
        {
            "variant": name,
            "source_sha256": variant["source_sha256"],
            "initial_sha256": hashlib.sha256(initial.read_bytes()).hexdigest(),
            "state_sha256": hashlib.sha256(states.read_bytes()).hexdigest(),
            "initial_active": len(active),
            "observed_first_step_deaths": len(dead),
            "deaths_with_initial_empty_resource_opportunity": len(opportunities),
            "opportunities": opportunities,
        }
    )
args.output.write_text(
    json.dumps({"variants": records, "scope": __doc__}, indent=2) + "\n"
)
