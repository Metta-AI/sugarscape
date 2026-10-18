"""Independently replay realized native moves, harvest, occupancy and regeneration."""

import argparse
import csv
import gzip
import hashlib
import json
from pathlib import Path

import numpy as np

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("trace", type=Path)
parser.add_argument("original", type=Path)
parser.add_argument("output", type=Path)
parser.add_argument(
    "--profile",
    choices=["calibration-pilot", "gradient-ensemble", "gradient-trace"],
    default="calibration-pilot",
)
args = parser.parse_args()
gradient = args.profile != "calibration-pilot"
traced = args.profile == "gradient-trace"
states, width, radius, seeds = (
    (25, 50, 3, range(3, 259)) if gradient else (50, 25, 6, range(3))
)
if traced:
    with (args.trace / "cases.csv").open() as handle:
        cases = list(csv.DictReader(handle))
    assert cases and len({row["case"] for row in cases}) == len(cases)
    declared_seeds = sorted({int(row["seed"]) for row in cases})
    assert declared_seeds == list(range(declared_seeds[0], declared_seeds[-1] + 1))
    assert 3 <= declared_seeds[0] <= declared_seeds[-1] <= 258
    coordinates = {
        (
            int(row["seed"]),
            int(row["parameter"]),
            float(row["step"]),
            int(row["direction"]),
        )
        for row in cases
    }
    perturbed = any(int(row["parameter"]) != 0 for row in cases)
    expected = (
        {
            (seed, parameter, step, direction)
            for seed in declared_seeds
            for parameter in range(1, 7)
            for step in [0.001, 0.01, 0.05]
            for direction in [-1, 1]
        }
        if perturbed
        else {(seed, 0, 0.0, 0) for seed in declared_seeds}
    )
    assert coordinates == expected and len(coordinates) == len(cases)
else:
    cases = [{"seed": seed, "case": f"seed-{seed}"} for seed in seeds]
if gradient:
    for line in (args.trace / "sha256.txt").read_text().splitlines():
        digest, name = line.split("  ", 1)
        assert Path(name).name == name
        assert hashlib.sha256((args.trace / name).read_bytes()).hexdigest() == digest
    with (args.trace / "passive-parity.csv").open() as handle:
        parity = list(csv.DictReader(handle))
    assert len(parity) == len(cases) * 6
    if traced:
        assert {(row["case"], int(row["component"])) for row in parity} == {
            (case["case"], component) for case in cases for component in range(1, 7)
        }
    else:
        assert {(int(row["seed"]), int(row["component"])) for row in parity} == {
            (seed, component) for seed in seeds for component in range(1, 7)
        }
    assert all(
        int(row["observations"])
        == states * (width * width if int(row["component"]) in [1, 6] else 100)
        for row in parity
    )

reports = []
for case in cases:
    seed = int(case["seed"])
    prefix = case["case"]
    for kind in [] if gradient else ["agents", "cells"]:
        assert (args.trace / f"{prefix}-{kind}.csv").read_bytes() == (
            args.original / f"{prefix}-{kind}.csv"
        ).read_bytes()
    agents = np.full((states, 100, 4), np.nan)
    boards = np.full((states, width, width), np.nan)
    occupancy = np.full_like(boards, np.nan)
    with (
        gzip.open(args.trace / f"{prefix}-agents.csv.gz", "rt")
        if traced
        else (args.trace / f"{prefix}-agents.csv").open()
    ) as f:
        for r in csv.DictReader(f):
            agents[int(r["time"]), int(r["agent"]) - 1] = [
                float(r[k]) for k in ["x", "y", "wealth", "alive"]
            ]
    with (
        gzip.open(args.trace / f"{prefix}-cells.csv.gz", "rt")
        if traced
        else (args.trace / f"{prefix}-cells.csv").open()
    ) as f:
        for r in csv.DictReader(f):
            index = (int(r["time"]), int(r["x"]) - 1, int(r["y"]) - 1)
            boards[index] = float(r["sugar"])
            occupancy[index] = float(r["occupied"])
    masks = np.full((100, 2 * radius + 1, 2 * radius + 1), np.nan)
    metabolism = np.full(100, np.nan)
    with (
        gzip.open(args.trace / f"{prefix}-parameters.csv.gz", "rt")
        if traced
        else (args.trace / f"{prefix}-parameters.csv").open()
    ) as f:
        for r in csv.DictReader(f):
            a = int(r["agent"]) - 1
            metabolism[a] = float(r["metabolism"])
            masks[a, int(r["vision_i"]) - 1, int(r["vision_j"]) - 1] = float(r["mask"])
    assert all(
        np.all(np.isfinite(v)) for v in [agents, boards, occupancy, masks, metabolism]
    )
    assert set(np.unique(masks)) <= {0.0, 1.0}
    if gradient:
        with (args.original / f"seed-{seed}.csv").open() as handle:
            original = list(csv.DictReader(handle))
        assert len(original) == 450
        for row in original:
            assert int(row["seed"]) == seed
            field = "primal"
            if traced and int(case["parameter"]) != 0:
                if int(row["parameter"]) != int(case["parameter"]) or float(
                    row["step"]
                ) != float(case["step"]):
                    continue
                field = "plus" if int(case["direction"]) == 1 else "minus"
            assert (
                abs(float(row[field]) - agents[int(row["time"]), :, 2].sum() / 100)
                < 1e-10
            )

    orders = np.full((states - 1, 100), -1, dtype=int)
    with (
        gzip.open(args.trace / f"{prefix}-orders.csv.gz", "rt")
        if traced
        else (args.trace / f"{prefix}-orders.csv").open()
    ) as f:
        for r in csv.DictReader(f):
            orders[int(r["transition"]) - 1, int(r["position"]) - 1] = (
                int(r["agent"]) - 1
            )
    assert all(sorted(row) == list(range(100)) for row in orders)
    board = boards[0].copy()
    cap = board.copy()
    occupied = np.zeros((width, width))
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
                    ((x + di - 1) % width, (y + dj - 1) % width)
                    for di in range(-radius, radius + 1)
                    for dj in range(-radius, radius + 1)
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
                occupied[(x - 1) % width, (y - 1) % width] = 0.0
                occupied[target] += 1.0
                new_wealth = wealth + board[target] - metabolism[a]
                board[target] = 0.0
                state[a] = [nx, ny, new_wealth, float(wealth >= 0)]
            else:
                occupied[(x - 1) % width, (y - 1) % width] = 0.0
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
            "case": case,
            "agent_updates": (states - 1) * 100,
            "cell_updates": (states - 1) * width * width,
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
    "profile": args.profile,
    "runs": reports,
    "scope": "Independent replay of declared cases using recorded activation order and realized destinations. Every live destination must maximize native masked score; random tie-selection probabilities are not reproduced. State, resource and occupancy updates are reconstructed. Calibration-pilot CSVs match original uninstrumented pilots; gradient aggregates match the corresponding retained baseline or plus/minus ensemble records and native passive-trace hashes match the ordinary histories. Not a paper-level verdict.",
}
(args.output / "audit.json").write_text(json.dumps(report, indent=2) + "\n")
print(
    json.dumps(
        {
            "profile": args.profile,
            "runs": len(reports),
            "agent_updates": sum(row["agent_updates"] for row in reports),
            "cell_updates": sum(row["cell_updates"] for row in reports),
            "outside_moves": sum(row["moves_outside_vision_mask"] for row in reports),
            "max_error": max(row["maximum_absolute_state_error"] for row in reports),
        }
    )
)
