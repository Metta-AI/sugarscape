"""Passive full-state observation of frozen independent input zero."""

import argparse
import csv
import gzip
import hashlib
import json
import platform
import sys
from pathlib import Path

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("source", type=Path)
parser.add_argument("output", type=Path)
args = parser.parse_args()
sys.path.insert(0, str(args.source))
from model import Model, Parameters

row = next(csv.DictReader((args.source / "params_sugarscape.csv").open()))
model = Model(
    Parameters(
        population=int(float(row["initial-population"])),
        mutation=float(row["pmut"]),
        maximum_sugar=int(float(row["maximum-sugar-endowment"])),
        maximum_spice=int(float(row["maximum-spice-endowment"])),
        reproduction=float(row["wealth-reproduction"]),
        seed=int(float(row["random-seed"])),
    )
)
with gzip.open(args.output, "xt") as stream:
    stream.write(
        json.dumps(
            {
                "platform": platform.platform(),
                "machine": platform.machine(),
                "python": platform.python_version(),
                "source_sha256": hashlib.sha256((args.source / "model.py").read_bytes()).hexdigest(),
                "observer_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            }
        )
        + "\n"
    )
    for observation in range(501):
        agents = [a.model_dump() for a in model.agents.values()]
        wealth = [
            [a["identifier"], a["sugar"], a["spice"], a["sugar_metabolism"], a["spice_metabolism"], a.pop("wealth")]
            for a in agents
        ]
        state = {
            "agents": agents,
            "random": model.random.getstate(),
            "parameters": model.parameters.model_dump(),
            "cells": model.cells,
            "capacity_sugar": list(model.capacity_sugar.items()),
            "capacity_spice": list(model.capacity_spice.items()),
            "sugar": list(model.sugar.items()),
            "spice": list(model.spice.items()),
            "occupied": list(model.occupied.items()),
            "next_id": model.next_id,
            "tick": model.tick,
            "prices": model.prices,
            "mean_price": model.mean_price,
        }
        assert set(vars(model)) == set(state)
        digest = hashlib.sha256(json.dumps(state, separators=(",", ":")).encode()).hexdigest()
        stream.write(
            json.dumps(
                {
                    "observation": observation,
                    "state_without_cached_wealth_sha256": digest,
                    "wealth": wealth,
                    "reported": model.observation(),
                },
                separators=(",", ":"),
            )
            + "\n"
        )
        model.step()
print("Completed 501 passive state observations")
