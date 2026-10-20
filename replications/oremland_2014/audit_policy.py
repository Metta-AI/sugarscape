"""Reconcile every tax event with policy coordinates and complete native trajectories."""

import argparse
from collections import Counter, defaultdict
import csv
from decimal import Decimal
import hashlib
import json
from pathlib import Path

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("run", type=Path)
parser.add_argument("seeds", type=int)
parser.add_argument("output", type=Path)
args = parser.parse_args()
policy = [Decimal(line) for line in (args.run / "policy.txt").read_text().splitlines()]
assert len(policy) == 200 and set(policy) <= {
    Decimal(0),
    Decimal("0.25"),
    Decimal("0.5"),
    Decimal("0.75"),
}
with (args.run / "runs/trajectory.csv").open() as stream:
    trajectories = list(csv.DictReader(stream))
assert len(trajectories) == args.seeds * 4 * 51
states = {}
for row in trajectories:
    key = (
        int(row["seed"]),
        int(row["phase"]),
        row["clipped"] == "true",
        int(row["step"]),
    )
    assert key not in states and row["clipped"] in {"true", "false"}
    assert len(row["state_sha256"]) == 64
    int(row["state_sha256"], 16)
    states[key] = row
payments = defaultdict(Decimal)
refunds = defaultdict(Decimal)
counts = Counter()
coverage = Counter()
events = {}
with (args.run / "runs/tax-events.csv").open() as stream:
    for row in csv.DictReader(stream):
        run_key = (
            int(row["seed"]),
            int(row["phase"]),
            row["clipped"] == "true",
            int(row["step"]),
        )
        assert run_key in states and row["clipped"] in {"true", "false"}
        numeric = {
            name: Decimal(row[name])
            for name in [
                "agent",
                "vision",
                "metabolism",
                "capacity",
                "cycle",
                "policy_index",
                "rate",
                "before",
                "paid",
                "after",
            ]
        }
        assert all(
            value == int(value) for name, value in numeric.items() if name != "rate"
        )
        event_key = (*run_key, int(numeric["agent"]))
        assert event_key not in events
        events[event_key] = numeric
        vision, metabolism, capacity = (
            int(numeric[name]) for name in ["vision", "metabolism", "capacity"]
        )
        assert 1 <= vision <= 5 and 1 <= metabolism <= 4 and 0 <= capacity <= 4
        seed, phase, clipped, step = run_key
        assert (step - 1) % 5 == phase
        cycle = (step - 1) // 5
        category = {
            (False, False): 0,
            (False, True): 1,
            (True, False): 2,
            (True, True): 3,
        }[(vision >= 4, metabolism >= 3)]
        index = 20 * cycle + 5 * category + capacity
        assert numeric["cycle"] == cycle and numeric["policy_index"] == index
        assert numeric["rate"] == policy[index]
        before = int(numeric["before"])
        quarter_rate = int(policy[index] * 4)
        paid = min(before, (quarter_rate * before + 3) // 4)
        if clipped:
            paid = max(0, paid)
        assert numeric["paid"] == paid and numeric["after"] == before - paid
        payments[run_key] += paid
        refunds[run_key] += max(0, -before)
        counts[run_key] += 1
        coverage[index] += 1
paired_states = 0
for seed in range(1, args.seeds + 1):
    for phase in [0, 4]:
        for clipped in [False, True]:
            previous_population, revenue, debt = Decimal(200), Decimal(0), Decimal(0)
            for step in range(51):
                key = (seed, phase, clipped, step)
                row = states[key]
                expected_events = (
                    int(previous_population)
                    if step > 0 and (step - 1) % 5 == phase
                    else 0
                )
                assert counts[key] == expected_events
                revenue += payments[key]
                debt += refunds[key]
                assert (
                    Decimal(row["total_tax"]) == revenue
                    and Decimal(row["debt_refund"]) == debt
                )
                population = Decimal(row["population"])
                assert (
                    population == int(population)
                    and 0 <= population <= previous_population
                )
                if step == 0:
                    assert population == 200
                previous_population = population
                if clipped:
                    literal = states[(seed, phase, False, step)]
                    assert row["state_sha256"] == literal["state_sha256"]
                    assert row["population"] == literal["population"]
                    assert revenue - Decimal(literal["total_tax"]) == debt
                    assert 0 <= debt <= 600
                    paired_states += 1
for key, row in events.items():
    seed, phase, clipped, step, agent = key
    if clipped:
        literal = events[(seed, phase, False, step, agent)]
        assert {
            name: value for name, value in row.items() if name not in {"paid", "after"}
        } == {
            name: value
            for name, value in literal.items()
            if name not in {"paid", "after"}
        }
report = {
    "complete_runs": args.seeds * 4,
    "observations": len(states),
    "validated_native_tax_events": len(events),
    "exact_paired_survivor_states": paired_states,
    "observed_policy_entries": len(coverage),
    "missing_policy_entries": sorted(set(range(200)) - set(coverage)),
    "event_counts_by_policy_entry": {
        str(index): count for index, count in sorted(coverage.items())
    },
    "sha256": {
        name: hashlib.sha256((args.run / name).read_bytes()).hexdigest()
        for name in [
            "policy.txt",
            "runs/trajectory.csv",
            "runs/tax-events.csv",
            "manifest.json",
            "exit.json",
        ]
    },
    "scope": "Complete generated heterogeneous-policy workflows, with independently reconstructed policy coordinates, payments, complete per-tax-step event counts, revenue totals, and paired survivor-state equality. No original control-vector or published ranking/optimization claim.",
}
assert json.loads((args.run / "exit.json").read_text())["exit_code"] == 0
with args.output.open("x") as stream:
    stream.write(json.dumps(report, indent=2) + "\n")
print(
    json.dumps(
        {
            key: value
            for key, value in report.items()
            if key not in {"sha256", "event_counts_by_policy_entry"}
        }
    )
)
