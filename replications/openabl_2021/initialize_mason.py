"""Independently reconstruct the released MASON Sugarscape initial state."""

import argparse
import hashlib
import json
import math
from pathlib import Path

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("native", type=Path)
parser.add_argument("output", type=Path)
parser.add_argument("--requested-cells", type=int, required=True)
parser.add_argument("--seed", type=int, default=0)
args = parser.parse_args()
width = math.isqrt(args.requested_cells)
assert width > 0
assert 0 <= args.seed < 2**32
mask = (1 << 32) - 1
state = [args.seed]
for i in range(1, 624):
    state.append((1812433253 * (state[-1] ^ (state[-1] >> 30)) + i) & mask)
index = 624
draws = 0


def draw():
    global index, draws
    if index == 624:
        for i in range(624):
            value = (state[i] & 0x80000000) | (state[(i + 1) % 624] & 0x7FFFFFFF)
            state[i] = state[(i + 397) % 624] ^ (value >> 1)
            if value & 1:
                state[i] ^= 0x9908B0DF
        index = 0
    value = state[index]
    index += 1
    draws += 1
    value ^= value >> 11
    value ^= (value << 7) & 0x9D2C5680
    value ^= (value << 15) & 0xEFC60000
    return (value ^ (value >> 18)) & mask


def integer(low, high):
    size = high - low + 1
    if size & (size - 1) == 0:
        return low + ((size * (draw() >> 1)) >> 31)
    bits = draw() >> 1
    value = bits % size
    while bits - value + size - 1 >= 2**31:
        bits = draw() >> 1
        value = bits % size
    return low + value


# MASON19 SimState.start primes its generator before initializing any agents.
for _ in range(1249):
    draw()

# The released printer emits folded floating constants with six significant
# digits. Reconstruct the generated C value, including that precision loss.
variance = float(format(0.025 * width * width, ".6g"))
cells = []
for x in range(width):
    for y in range(width):
        occupied = (((draw() >> 6) << 27) + (draw() >> 5)) / 2**53 < 0.1
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
            "seed": args.seed,
            "final_rng_index": index,
            "final_rng_state_sha256": hashlib.sha256(
                json.dumps(state).encode()
            ).hexdigest(),
            "differences": differences,
            "native_sha256": hashlib.sha256(args.native.read_bytes()).hexdigest(),
            "source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            "scope": "MASON19 MT19937 seed expansion,1249-draw startup, and default generated initialization reconstructed independently. Does not establish historical benchmark seeds.",
            "completed_study": False,
        },
        indent=2,
    )
    + "\n"
)
assert not differences, f"{len(differences)} initialization field differences"
print(f"Matched {len(cells) * 8} initialization fields using {draws} draws")
