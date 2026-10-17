"""Independently replay realized native moves, harvest, occupancy and regeneration."""

import argparse
import csv
import json
from pathlib import Path

import numpy as np

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("trace", type=Path)
parser.add_argument("original", type=Path)
parser.add_argument("output", type=Path)
args = parser.parse_args()
reports = []
for seed in range(3):
    prefix = f"seed-{seed}"
    for kind in ["agents", "cells"]:
        assert (args.trace / f"{prefix}-{kind}.csv").read_bytes() == (
            args.original / f"{prefix}-{kind}.csv"
        ).read_bytes()
    agents = np.full((50, 100, 4), np.nan)
    boards = np.full((50, 25, 25), np.nan)
    occupancy = np.full_like(boards, np.nan)
    with (args.trace / f"{prefix}-agents.csv").open() as f:
        for r in csv.DictReader(f):
            agents[int(r["time"]), int(r["agent"]) - 1] = [
                float(r[k]) for k in ["x", "y", "wealth", "alive"]
            ]
    with (args.trace / f"{prefix}-cells.csv").open() as f:
        for r in csv.DictReader(f):
            index = (int(r["time"]), int(r["x"]) - 1, int(r["y"]) - 1)
            boards[index] = float(r["sugar"])
            occupancy[index] = float(r["occupied"])
    masks = np.full((100, 13, 13), np.nan)
    metabolism = np.full(100, np.nan)
    with (args.trace / f"{prefix}-parameters.csv").open() as f:
        for r in csv.DictReader(f):
            a = int(r["agent"]) - 1
            metabolism[a] = float(r["metabolism"])
            masks[a, int(r["vision_i"]) - 1, int(r["vision_j"]) - 1] = float(r["mask"])
    assert all(
        np.all(np.isfinite(v)) for v in [agents, boards, occupancy, masks, metabolism]
    )
    assert set(np.unique(masks)) <= {0.0, 1.0}
    orders = np.full((49, 100), -1, dtype=int)
    with (args.trace / f"{prefix}-orders.csv").open() as f:
        for r in csv.DictReader(f):
            orders[int(r["transition"]) - 1, int(r["position"]) - 1] = (
                int(r["agent"]) - 1
            )
    assert all(sorted(row) == list(range(100)) for row in orders)
    board = boards[0].copy()
    cap = board.copy()
    occupied = np.zeros((25, 25))
    state = agents[0].copy()
    for x, y, _, _ in state:
        occupied[int(x) - 1, int(y) - 1] = 1.0
    assert np.array_equal(occupied, occupancy[0])
    exceptional_moves = []
    outside = 0
    zero_score = 0
    occupied_moves = 0
    living_moves = 0
    max_error = 0.0
    for time, order in enumerate(orders, 1):
        for a in order:
            x, y, wealth, alive = state[a]
            x = int(x)
            y = int(y)
            if alive:
                destinations = [
                    ((x + di - 1) % 25, (y + dj - 1) % 25)
                    for di in range(-6, 7)
                    for dj in range(-6, 7)
                ]
                scores = [
                    board[i, j] * (1 - occupied[i, j]) * m
                    for (i, j), m in zip(destinations, masks[a].flat, strict=True)
                ]
                nx, ny = map(int, agents[time, a, :2])
                target = (nx - 1, ny - 1)
                index = destinations.index(target)
                assert scores[index] == max(scores), (seed, time, a, "nonmaximal move")
                zero_score += max(scores) == 0
                outside += masks[a].flat[index] == 0
                occupied_moves += occupied[target] != 0
                living_moves += 1
                if masks[a].flat[index] == 0 or occupied[target] != 0:
                    exceptional_moves.append(
                        {
                            "transition": time,
                            "agent": int(a) + 1,
                            "origin": [x, y],
                            "destination": [nx, ny],
                            "vision_mask": float(masks[a].flat[index]),
                            "maximum_score": float(max(scores)),
                            "destination_occupancy": float(occupied[target]),
                        }
                    )
                occupied[(x - 1) % 25, (y - 1) % 25] = 0.0
                occupied[target] += 1.0
                new_wealth = wealth + board[target] - metabolism[a]
                board[target] = 0.0
                state[a] = [nx, ny, new_wealth, float(wealth >= 0)]
            else:
                occupied[(x - 1) % 25, (y - 1) % 25] = 0.0
                state[a] = [0, 0, wealth, 0]
            error = float(np.max(np.abs(state[a] - agents[time, a])))
            max_error = max(max_error, error)
            assert error < 1e-10, (seed, time, a, "state", error)
        board = np.minimum(board + 1.0, cap)
        error = float(np.max(np.abs(board - boards[time])))
        max_error = max(max_error, error)
        assert error < 1e-10, (seed, time, "board", error)
        assert np.array_equal(occupied, occupancy[time]), (seed, time, "occupancy")
    reports.append(
        {
            "seed": seed,
            "agent_updates": 4900,
            "cell_updates": 30625,
            "living_moves": living_moves,
            "all_zero_maximum_choices": int(zero_score),
            "moves_outside_vision_mask": int(outside),
            "moves_to_marked_occupied_cells": int(occupied_moves),
            "maximum_absolute_state_error": max_error,
            "exceptional_moves": exceptional_moves,
        }
    )
args.output.mkdir(parents=True, exist_ok=False)
report = {
    "runs": reports,
    "scope": "Independent replay using recorded activation order and realized destinations. Every live destination must maximize native masked score; random tie-selection probabilities are not reproduced. State, resource and occupancy updates are reconstructed. Trace CSVs exactly match original uninstrumented pilots. Not a paper-level verdict.",
}
(args.output / "audit.json").write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps(report))
