"""Replay the complete four-stage model from a native initial-state snapshot."""

import argparse
import dataclasses
import hashlib
import json
from pathlib import Path


@dataclasses.dataclass
class Cell:
    pos: list[float]
    target_pos: list[float]
    agent_id: int
    state: int
    sugar_level: int
    metabolism: int
    env_sugar_level: int
    max_env_sugar_level: int


parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("initial", type=Path)
parser.add_argument("expected", type=Path)
parser.add_argument("output", type=Path)
parser.add_argument("--steps", type=int, required=True)
parser.add_argument("--buffer", choices=["copy", "stale"], required=True)
args = parser.parse_args()
assert args.steps > 0
current = [Cell(**row) for row in json.loads(args.initial.read_text())["Agent"]]
other = [dataclasses.replace(cell) for cell in current]
# Released Sugarscape cells have fixed, unique half-integer grid centers. At radius
# 1.5, exactly the nine adjacent offsets qualify; preserve native array order.
positions = [tuple(cell.pos) for cell in current]
assert all(
    len(pos) == 2 and all(value - 0.5 == int(value - 0.5) for value in pos)
    for pos in positions
)
indices = {pos: i for i, pos in enumerate(positions)}
assert len(indices) == len(current)
neighbors = [
    sorted(
        indices[(x + dx, y + dy)]
        for dx in (-1, 0, 1)
        for dy in (-1, 0, 1)
        if (x + dx, y + dy) in indices
    )
    for x, y in positions
]
for _ in range(args.steps):
    for stage in range(4):
        if args.buffer == "copy":
            other = [dataclasses.replace(cell) for cell in current]
        for i, cell in enumerate(current):
            out = other[i]
            if stage == 0:
                sugar = cell.env_sugar_level
                if cell.state == 1:
                    wealth = cell.sugar_level + sugar - cell.metabolism
                    sugar = 0
                    if wealth <= 0:
                        out.state, out.agent_id = 0, -1
                        out.sugar_level, out.metabolism = 0, 0
                    else:
                        out.state, out.sugar_level = 3, wealth
                out.env_sugar_level = min(sugar + 1, cell.max_env_sugar_level)
            elif stage == 1 and cell.state == 3:
                best_sugar, best_pos = -1, [0.0, 0.0]
                for j in neighbors[i]:
                    candidate = current[j]
                    if (
                        j != i
                        and candidate.state == 0
                        and candidate.env_sugar_level > best_sugar
                    ):
                        best_sugar, best_pos = candidate.env_sugar_level, candidate.pos
                if best_sugar > cell.env_sugar_level:
                    out.state, out.target_pos = 2, best_pos
                else:
                    out.state = 1
            elif stage == 2 and cell.state == 0:
                for j in neighbors[i]:
                    candidate = current[j]
                    if candidate.state == 2 and candidate.target_pos == cell.pos:
                        if candidate.agent_id >= 0:
                            out.state, out.agent_id = 1, candidate.agent_id
                            out.sugar_level = candidate.sugar_level
                            out.metabolism = candidate.metabolism
                        break
            elif stage == 3 and cell.state == 2:
                moved = any(
                    current[j].state == 1 and current[j].agent_id == cell.agent_id
                    for j in neighbors[i]
                )
                if moved:
                    out.state, out.agent_id = 0, -1
                    out.sugar_level, out.metabolism = 0, 0
                else:
                    out.state = 1
        current, other = other, current
actual = [dataclasses.asdict(cell) for cell in current]
expected = json.loads(args.expected.read_text())["Agent"]
assert len(actual) == len(expected)
differences = [
    {"cell": i, "field": field, "native": native[field], "replay": replay[field]}
    for i, (native, replay) in enumerate(zip(expected, actual, strict=True))
    for field in native
    if native[field] != replay[field]
]
result = {
    "cells": len(actual),
    "steps": args.steps,
    "stages": 4,
    "buffer": args.buffer,
    "fields_compared": len(actual) * len(actual[0]),
    "differences": differences,
    "initial_sha256": hashlib.sha256(args.initial.read_bytes()).hexdigest(),
    "native_final_sha256": hashlib.sha256(args.expected.read_bytes()).hexdigest(),
    "replay_source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    "scope": "Deterministic replay from native initialization; does not validate initialization RNG or paper timings.",
    "completed_study": False,
}
args.output.write_text(json.dumps(result, indent=2) + "\n")
assert not differences, f"{len(differences)} field differences"
print(
    f"Matched {result['fields_compared']} fields after {args.steps} steps ({args.buffer} buffers)"
)
