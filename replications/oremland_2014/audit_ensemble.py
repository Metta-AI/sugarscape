"""Audit complete paired native workflows without treating controls as paper results."""

import argparse
import csv
import hashlib
import json
from pathlib import Path

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("trajectory", type=Path)
parser.add_argument("seeds", type=int)
parser.add_argument("output", type=Path)
args = parser.parse_args()
with args.trajectory.open(newline="") as stream:
    rows = list(csv.DictReader(stream))
assert len(rows) == args.seeds * 16 * 51
indexed = {}
for row in rows:
    key = (
        int(row["seed"]),
        float(row["rate"]),
        int(row["phase"]),
        row["clipped"] == "true",
        int(row["step"]),
    )
    assert row["clipped"] in {"true", "false"} and key not in indexed
    assert 0 <= float(row["population"]) <= 200
    assert float(row["population"]).is_integer()
    assert len(row["state_sha256"]) == 64 and int(row["state_sha256"], 16) >= 0
    indexed[key] = row
paired = 0
finals = []
for seed in range(1, args.seeds + 1):
    initial = set()
    for rate in [0, 0.25, 0.5, 0.75]:
        for phase in [0, 4]:
            previous_population = 200
            for step in range(51):
                literal = indexed[(seed, rate, phase, False, step)]
                clipped = indexed[(seed, rate, phase, True, step)]
                assert literal["state_sha256"] == clipped["state_sha256"]
                assert literal["population"] == clipped["population"]
                assert literal["debt_refund"] == clipped["debt_refund"]
                population = float(literal["population"])
                assert population <= previous_population
                previous_population = population
                difference = float(clipped["total_tax"]) - float(literal["total_tax"])
                assert difference == float(literal["debt_refund"])
                assert 0 <= difference <= 600 and float(clipped["total_tax"]) >= 0
                if rate == 0:
                    assert float(clipped["total_tax"]) == 0
                if step == 0:
                    assert population == 200 and difference == 0
                    assert float(literal["total_tax"]) == 0
                    initial.add(literal["state_sha256"])
                paired += 1
            finals.append(
                {
                    "seed": seed,
                    "rate": rate,
                    "phase": phase,
                    "population": int(population),
                    "literal_revenue": float(literal["total_tax"]),
                    "clipped_revenue": float(clipped["total_tax"]),
                    "refund": difference,
                }
            )
    assert len(initial) == 1
report = {
    "trajectory_sha256": hashlib.sha256(args.trajectory.read_bytes()).hexdigest(),
    "seeds": args.seeds,
    "complete_50_step_runs": args.seeds * 16,
    "observations": len(rows),
    "exact_paired_survivor_states": paired,
    "minimum_refund": min(row["refund"] for row in finals),
    "maximum_refund": max(row["refund"] for row in finals),
    "finals": finals,
    "scope": "Native NetLogo reconstruction controls: four uniform tax rates, two clock phases, literal versus clipped payment. Original 100 control schedules, reduced grids, and optimizer not reproduced. No whole-paper completion claim.",
}
with args.output.open("x") as stream:
    stream.write(json.dumps(report, indent=2) + "\n")
print(json.dumps({key: value for key, value in report.items() if key != "finals"}))
