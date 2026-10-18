"""Independently reconstruct the released C Sugarscape initial state."""

import argparse
import hashlib
import json
import math
from pathlib import Path

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("native", type=Path)
parser.add_argument("output", type=Path)
parser.add_argument("--requested-cells", type=int, required=True)
args = parser.parse_args()
width = math.isqrt(args.requested_cells)
assert width > 0
state = [0xDEADBEEF, 0xBEEFDEAD]
mask = (1 << 64) - 1
draws = 0


def draw():
    global draws
    draws += 1
    x, y = state
    state[0] = y
    x ^= (x << 23) & mask
    state[1] = x ^ y ^ (x >> 17) ^ (y >> 26)
    return (state[1] + y) & mask


def integer(low, high):
    size = high - low + 1
    if size & (size - 1) == 0:
        # Preserve the released algorithm, including its missing low offset.
        return draw() & (size - 1)
    maximum = (1 << 32) - 1
    limit = maximum - maximum % size
    value = draw() & maximum
    while value >= limit:
        value = draw() & maximum
    return low + value % size


# The released printer emits folded floating constants with six significant
# digits. Reconstruct the generated C value, including that precision loss.
variance = float(format(0.025 * width * width, ".6g"))
cells = []
for x in range(width):
    for y in range(width):
        occupied = float(draw()) / float(mask) < 0.1
        capacity = 0
        for fraction in [0.25, 0.75]:
            distance = math.sqrt(
                (x - fraction * width) ** 2 + (y - fraction * width) ** 2
            )
            capacity = int(
                capacity + 50 * math.exp(-distance * distance / (2 * variance))
            )
        wealth = integer(1, 10) if occupied else 0
        cells.append(
            {
                "pos": [x + 0.5, y + 0.5],
                "target_pos": [0.0, 0.0],
                "agent_id": x * width + y,
                "state": int(occupied),
                "sugar_level": wealth,
                "metabolism": int(occupied),
                "env_sugar_level": integer(0, capacity),
                "max_env_sugar_level": capacity,
            }
        )
native = json.loads(args.native.read_text())["Agent"]
assert len(native) == len(cells)
differences = [
    {"cell": i, "field": key, "native": a[key], "reconstructed": b[key]}
    for i, (a, b) in enumerate(zip(native, cells, strict=True))
    for key in a
    if a[key] != b[key]
]
args.output.write_text(
    json.dumps(
        {
            "requested_cells": args.requested_cells,
            "actual_cells": len(cells),
            "fields_compared": len(cells) * 8,
            "random_draws": draws,
            "generated_variance": variance,
            "final_rng_state": state,
            "differences": differences,
            "native_sha256": hashlib.sha256(args.native.read_bytes()).hexdigest(),
            "source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            "scope": "Released C RNG and default initialization reconstructed independently; does not establish intended statistical properties or other backend RNG equivalence.",
            "completed_study": False,
        },
        indent=2,
    )
    + "\n"
)
assert not differences, f"{len(differences)} initialization field differences"
print(f"Matched {len(cells) * 8} initialization fields using {draws} draws")
