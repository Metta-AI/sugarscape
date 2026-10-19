"""Compare complete native and independent movement-boundary ticks."""

import argparse
import csv
import hashlib
import json
from pathlib import Path

from model import Agent, Model, Parameters

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("native", type=Path)
parser.add_argument("output", type=Path)
args = parser.parse_args()
rows = []
for vision in [-3, -1, 0, 1, 2, 6]:
    for offset in [1, 2]:
        model = Model(
            Parameters(
                population=0,
                mutation=0,
                maximum_sugar=10,
                maximum_spice=10,
                reproduction=100000,
                seed=0,
            )
        )
        for values in [
            model.sugar,
            model.spice,
            model.capacity_sugar,
            model.capacity_spice,
        ]:
            for cell in model.cells:
                values[cell] = 0
            values[25 + offset, 25] = 4
        agent = Agent(
            identifier=0,
            x=25,
            y=25,
            sugar=10,
            spice=10,
            sugar_metabolism=1,
            spice_metabolism=1,
            vision=vision,
            wealth=10,
        )
        model.agents[0] = agent
        model.occupied[25, 25] = 0
        model.next_id = 1
        model.step()
        rows.append(
            {
                "vision": vision,
                "offset": offset,
                "tick": model.tick,
                "x": agent.x,
                "y": agent.y,
                "sugar": agent.sugar,
                "spice": agent.spice,
            }
        )
with args.native.open() as stream:
    native = list(csv.DictReader(stream))
assert len(native) == len(rows) == 12
for original, independent in zip(native, rows):
    assert all(float(original[name]) == value for name, value in independent.items())
    assert float(original["vision_points"]) == max(0, independent["vision"]) * 4
args.output.mkdir(exist_ok=False)
with (args.output / "independent.csv").open("w") as stream:
    writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
    writer.writeheader()
    writer.writerows(rows)
root = Path(__file__).resolve().parent
(args.output / "audit.json").write_text(
    json.dumps(
        {
            "native_complete_ticks": 12,
            "independent_complete_ticks": 12,
            "shared_fields_exact": 84,
            "native_vision_point_counts_checked": 12,
            "native_sha256": hashlib.sha256(args.native.read_bytes()).hexdigest(),
            "source_sha256": {
                name: hashlib.sha256((root / name).read_bytes()).hexdigest()
                for name in ["model.py", "VisionProbe.java", "verify_vision.py"]
            },
            "scope": "Controlled whole-model ticks. Negative, zero and positive vision with an isolated food patch at distances one and two. No stochastic ensemble or paper-level equivalence claim.",
        },
        indent=2,
    )
    + "\n"
)
print("12 complete ticks and84 shared fields match exactly.")
