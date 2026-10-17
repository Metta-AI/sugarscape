"""Execute legal positive-probability paths in the appendix's full Sugarscape model.

Choices are deliberately controlled witnesses, not samples from the stationary law.
"""

import argparse
import hashlib
import json
import math
from pathlib import Path

import numpy as np
from PIL import Image

from model import Agent, Model


parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("figure2", type=Path)
parser.add_argument("output", type=Path)
args = parser.parse_args()
figure_bytes = args.figure2.read_bytes()
assert (
    hashlib.sha256(figure_bytes).hexdigest()
    == "c53a23ca2c5fce8517cd77ebf61d5a703ec020723dc5d468003062d90df67fa9"
)
image = np.asarray(Image.open(args.figure2).convert("RGB"))
yellow = np.all(image == [255, 255, 0], axis=2)
counts = yellow[6:406, 3:403].reshape(50, 8, 50, 8).sum(axis=(1, 3))
# One radius-three marker has four extra edge pixels; retain this anomaly explicitly.
pixel_to_capacity = {0: 0, 4: 1, 12: 2, 32: 3, 36: 3, 52: 4}
assert set(np.unique(counts)) == set(pixel_to_capacity)
capacity_array = np.array([[pixel_to_capacity[int(v)] for v in row] for row in counts])
desert = capacity_array == 0
interior = desert.copy()
for axis in (0, 1):
    for direction in (-1, 1):
        interior &= np.roll(desert, direction, axis=axis)
assert int(interior.sum()) == 305
safe_sites = list(map(int, np.flatnonzero(interior)))
sites = safe_sites[:250]
capacity = list(map(int, capacity_array.flat))
args.output.mkdir(parents=True, exist_ok=False)
np.savetxt(args.output / "capacity.csv", capacity_array, delimiter=",", fmt="%d")
traces = []
results = []

for period, wealth, maximum_age in ((5, 5, 99), (6, 6, 100)):
    model = Model(capacity, [Agent(p, 1, 1, 1, 95) for p in sites], capacity, period)
    initial_hash = model.state_hash()

    def return_birth(index, occupied):
        return Agent(sites[index], 1, 1, wealth, maximum_age)

    for time in range(period + 1):
        traces.append(model.observation(f"return-{period}", time))
        if time < period:
            model.step(return_birth)
    assert (
        model.state_hash() == initial_hash
        and model.births == 250
        and model.harvest == 0
    )
    results.append(
        {
            "period": period,
            "return_state_sha256": initial_hash,
            "births": model.births,
            "log_choice_probability": model.log_choice_probability,
        }
    )

# Establish that the common return state itself is reachable from a legal initial state.
model = Model(capacity, [Agent(p, 1, 1, 5, 99) for p in sites], capacity, 0)
for time in range(5):
    traces.append(model.observation("initial-reachability", time))
    if time < 4:
        model.step(return_birth)
assert model.births == 0 and model.state_hash() == results[0]["return_state_sha256"]
assert results[0]["return_state_sha256"] == results[1]["return_state_sha256"]
assert math.gcd(*(row["period"] for row in results)) == 1

(args.output / "trajectory.jsonl").write_text(
    "".join(json.dumps(row) + "\n" for row in traces)
)
report = {
    "agents": 250,
    "cells": 2500,
    "safe_desert_sites": len(safe_sites),
    "return_paths": results,
    "return_period_gcd": 1,
    "initial_state_to_return_state_steps": 4,
    "initial_state_path_births": model.births,
    "capacity_raster_anomaly": {
        "cell_row_column": np.argwhere(counts == 36).tolist(),
        "observed_yellow_pixels": 36,
        "interpreted_capacity": 3,
        "reason": "Radius-three shape plus four edge pixels. Return paths harvest zero; only desert mask affects them.",
    },
    "figure2_sha256": hashlib.sha256(figure_bytes).hexdigest(),
    "model_sha256": hashlib.sha256(
        Path(__file__).with_name("model.py").read_bytes()
    ).hexdigest(),
    "runner_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    "scope": "Two legal return witnesses in the full specified-size model; establishes aperiodicity of this state's class only. Global irreducibility remains unproved.",
}
(args.output / "report.json").write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps(report))
