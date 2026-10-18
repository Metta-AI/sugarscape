"""Audit complete reduced-model workflows, map orientation, classes, and taxes."""

import argparse
from collections import Counter, defaultdict
import csv
from decimal import Decimal
from fractions import Fraction
import gzip
import hashlib
import json
from math import floor
from pathlib import Path

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("experiment", type=Path)
parser.add_argument(
    "reference", type=Path, help="Published heterogeneous policy evidence"
)
parser.add_argument("output", type=Path)
args = parser.parse_args()
root = args.experiment
protocol = json.loads((root / "protocol.json").read_text())
qualification = json.loads((root / "qualification-protocol.json").read_text())
assert json.loads((root / "qualification-exit.json").read_text())["exit_code"] == 0
assert (
    hashlib.sha256((root / "protocol.json").read_bytes()).hexdigest()
    == qualification["protocol_sha256"]
)
full = [
    int(value)
    for value in (root / "50-pixel_centers-nearest/sugar-map.txt").read_text().split()
]
assert len(full) == 2500
reference_manifest = json.loads((args.reference / "manifest.json").read_text())
with gzip.open(args.reference / "trajectory.csv.gz", "rt") as stream:
    reference_states = [row for row in csv.DictReader(stream) if int(row["seed"]) <= 2]
with gzip.open(args.reference / "tax-events.csv.gz", "rt") as stream:
    reference_events = [row for row in csv.DictReader(stream) if int(row["seed"]) <= 2]
reports = []
all_aliases = defaultdict(list)
for model in protocol["models"]:
    path = root / model["name"]
    assert (
        hashlib.sha256((path / "oremland.nlogo").read_bytes()).hexdigest()
        == model["model_sha256"]
    )
    assert (
        hashlib.sha256((path / "sugar-map.txt").read_bytes()).hexdigest()
        == model["landscape_sha256"]
    )
    all_aliases[(model["model_sha256"], model["landscape_sha256"])].append(
        model["name"]
    )
assert len(qualification["selected_models"]) == len(all_aliases) == 12
seen_models = set()
for name in qualification["selected_models"]:
    model = next(row for row in protocol["models"] if row["name"] == name)
    fingerprint = (model["model_sha256"], model["landscape_sha256"])
    assert fingerprint not in seen_models
    seen_models.add(fingerprint)
    path = root / name
    run = path / "qualification"
    assert json.loads((run / "exit.json").read_text())["exit_code"] == 0
    manifest = json.loads((run / "manifest.json").read_text())
    assert manifest["model_sha256"] == model["model_sha256"]
    assert manifest["jars"] == reference_manifest["jars"]
    assert (run / "policy.txt").read_bytes() == (
        args.reference / "policy.txt"
    ).read_bytes()
    policy = [Decimal(value) for value in (run / "policy.txt").read_text().split()]
    width, population = model["width"], model["initial_population"]
    assert population == 200 * Fraction(width, 50) ** 2
    if model["mapping"] == "pixel_centers":
        indices = [
            floor((Fraction(i) + Fraction(1, 2)) * 50 / width) for i in range(width)
        ]
    else:
        indices = [
            floor(Fraction(i * 49, width - 1) + Fraction(1, 2)) for i in range(width)
        ]
    assert indices == model["source_indices"]
    expected_map = {
        (x, width - 1 - row): full[indices[row] * 50 + indices[x]]
        for row in range(width)
        for x in range(width)
    }
    conditions = {
        (seed, phase, clipping)
        for seed in [1, 2]
        for phase in [0, 4]
        for clipping in ["false", "true"]
    }
    initial = {}
    occupied = defaultdict(set)
    with (run / "runs/initial-agents.csv").open() as stream:
        for row in csv.DictReader(stream):
            key = (int(row["seed"]), int(row["phase"]), row["clipped"])
            assert key in conditions
            values = {
                field: Decimal(value)
                for field, value in row.items()
                if field not in ["seed", "phase", "clipped"]
            }
            assert all(value == int(value) for value in values.values())
            agent = int(values["agent"])
            assert 0 <= agent < population and (*key, agent) not in initial
            coordinate = (int(values["x"]), int(values["y"]))
            assert coordinate in expected_map and coordinate not in occupied[key]
            occupied[key].add(coordinate)
            assert 5 <= values["sugar"] <= 25 and 1 <= values["metabolism"] <= 4
            original = int(values["original_vision"])
            assert 1 <= original <= 5
            assert values["vision"] == model["radius_by_original_vision"][original - 1]
            assert values["vision_point_count"] == 4 * values["vision"]
            initial[(*key, agent)] = values
    assert len(initial) == 8 * population and all(
        len(occupied[key]) == population for key in conditions
    )
    patch_seen = set()
    with (run / "runs/initial-patches.csv").open() as stream:
        for row in csv.DictReader(stream):
            key = (int(row["seed"]), int(row["phase"]), row["clipped"])
            coordinate = (int(Decimal(row["x"])), int(Decimal(row["y"])))
            assert key in conditions and (*key, *coordinate) not in patch_seen
            patch_seen.add((*key, *coordinate))
            assert (
                Decimal(row["capacity"])
                == Decimal(row["sugar"])
                == expected_map[coordinate]
            )
    assert len(patch_seen) == 8 * width * width
    with (run / "runs/trajectory.csv").open() as stream:
        trajectory = list(csv.DictReader(stream))
    states = {
        (int(row["seed"]), int(row["phase"]), row["clipped"], int(row["step"])): row
        for row in trajectory
    }
    assert len(states) == len(trajectory) == 8 * 51
    assert set(states) == {(*key, step) for key in conditions for step in range(51)}
    payments, refunds, counts = defaultdict(Decimal), defaultdict(Decimal), Counter()
    event_seen = set()
    with (run / "runs/tax-events.csv").open() as stream:
        events = list(csv.DictReader(stream))
    for row in events:
        condition = (int(row["seed"]), int(row["phase"]), row["clipped"])
        step = int(row["step"])
        key = (*condition, step)
        assert key in states and (step - 1) % 5 == condition[1]
        values = {
            field: Decimal(value)
            for field, value in row.items()
            if field not in ["seed", "phase", "clipped", "step"]
        }
        assert all(
            value == int(value) for field, value in values.items() if field != "rate"
        )
        agent = int(values["agent"])
        assert (*key, agent) not in event_seen
        event_seen.add((*key, agent))
        attributes = initial[(*condition, agent)]
        assert (
            values["vision"] == attributes["vision"]
            and values["metabolism"] == attributes["metabolism"]
        )
        category = 2 * int(attributes["original_vision"] > 3) + int(
            attributes["metabolism"] > 2
        )
        capacity = int(values["capacity"])
        assert 0 <= capacity <= 4
        index = 20 * ((step - 1) // 5) + 5 * category + capacity
        assert (
            values["cycle"] == (step - 1) // 5
            and values["policy_index"] == index
            and values["rate"] == policy[index]
        )
        before = int(values["before"])
        assert before >= -3
        paid = min(before, (before * int(policy[index] * 4) + 3) // 4)
        if condition[2] == "true":
            paid = max(0, paid)
        assert values["paid"] == paid and values["after"] == before - paid
        payments[key] += paid
        refunds[key] -= min(0, before)
        counts[key] += 1
    for condition in conditions:
        previous, income, refund = population, Decimal(0), Decimal(0)
        for step in range(51):
            key = (*condition, step)
            row = states[key]
            assert 0 <= Decimal(row["population"]) <= previous
            if step == 0:
                assert Decimal(row["population"]) == population
            if step > 0 and (step - 1) % 5 == condition[1]:
                assert counts[key] == previous
            else:
                assert counts[key] == 0
            income += payments[key]
            refund += refunds[key]
            assert (
                Decimal(row["total_tax"]) == income
                and Decimal(row["debt_refund"]) == refund
            )
            previous = Decimal(row["population"])
            other = states[(condition[0], condition[1], "true", step)]
            assert row["state_sha256"] == other["state_sha256"]
            if condition[2] == "false":
                assert Decimal(other["total_tax"]) - income == refund
    if width == 50:
        assert trajectory == reference_states and events == reference_events
    reports.append(
        {
            "model": name,
            "aliases": all_aliases[fingerprint],
            "width": width,
            "initial_population": population,
            "complete_runs": 8,
            "state_observations": len(states),
            "initial_agent_observations": len(initial),
            "initial_patch_observations": len(patch_seen),
            "tax_events": len(events),
            "full_size_reference_exact": width == 50,
            "sha256": {
                str(file.relative_to(run)): hashlib.sha256(
                    file.read_bytes()
                ).hexdigest()
                for file in sorted(run.rglob("*"))
                if file.is_file()
            },
        }
    )
report = {
    "distinct_models": len(reports),
    "parameter_cases": len(protocol["models"]),
    "complete_native_runs": sum(row["complete_runs"] for row in reports),
    "state_observations": sum(row["state_observations"] for row in reports),
    "tax_events": sum(row["tax_events"] for row in reports),
    "models": reports,
    "scope": "End-to-end qualification of declared reduction sensitivity cases, including unchanged full-size regression. This does not validate the unpublished author reduction conventions or reproduce Figure 10 rankings.",
}
with args.output.open("x") as stream:
    stream.write(json.dumps(report, indent=2) + "\n")
print(json.dumps({key: value for key, value in report.items() if key != "models"}))
