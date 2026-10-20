"""Independently audit long evolutionary trajectories and declared seed-level windows."""

import argparse
from collections import Counter
import csv
import hashlib
import json
import math
from pathlib import Path
from typing import Literal

import numpy as np
from pydantic import BaseModel, ConfigDict, Field
from scipy.stats import t


class Completion(BaseModel):
    model_config = ConfigDict(extra="forbid")
    scenario: Literal["stable", "chaotic"]
    seed: int = Field(ge=0, lt=100)
    final_cycle: int = Field(ge=1, le=100000)
    final_population: int = Field(ge=0, le=2500)
    observations: int = Field(ge=1, le=1001)
    sha256: dict[str, str]


parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("experiment", type=Path)
parser.add_argument("output", type=Path)
parser.add_argument(
    "--completed-prefix",
    action="store_true",
    help="Audit retained completed runs only; never compute across-seed statistics in this mode",
)
args = parser.parse_args()
root = args.experiment.resolve()
assert not args.output.exists()
protocol = json.loads((root / "protocol.json").read_text())
assert protocol["cycles"] == 100000 and protocol["record_every"] == 100
assert protocol["seeds"] == list(range(100))
assert protocol["scenarios"] == {"stable": 10, "chaotic": 1}
assert protocol["windows"] == [[35100, 50000], [75100, 100000]]
manifest = json.loads((root / "manifest.json").read_text())
for name, digest in manifest["sha256"].items():
    assert hashlib.sha256((root / name).read_bytes()).hexdigest() == digest
qualification = json.loads((root / "qualification.json").read_text())
assert qualification == {
    "complete_native_pairs": 2,
    "cycles_per_pair": 5000,
    "aggregate_and_individual_byte_exact": True,
    "sampled_joint_counts_exact": True,
}
ledger = (root / "completed.jsonl").read_bytes()
records = [Completion.model_validate_json(line) for line in ledger.splitlines()]
expected = [
    (scenario, seed) for seed in range(100) for scenario in ["stable", "chaotic"]
]
assert records and [(r.scenario, r.seed) for r in records] == expected[: len(records)]
if not args.completed_prefix:
    assert len(records) == 200, "Complete analysis requires all 200 runs"
    assert json.loads((root / "complete.json").read_text())["complete_runs"] == 200
metrics = ["population", "wealth", "mean_age", "gini"]
per_seed = []
for record in records:
    directory = root / "runs" / f"{record.scenario}-{record.seed}"
    assert set(record.sha256) == {
        "exit.json",
        "aggregate.csv",
        "observations.csv",
        "traits.csv",
        "stderr",
    }
    for name, digest in record.sha256.items():
        assert hashlib.sha256((directory / name).read_bytes()).hexdigest() == digest
    terminal = json.loads((directory / "exit.json").read_text())
    assert terminal["exit_code"] == 0
    assert terminal["command"] == [
        str(root / "model/sparse"),
        str(record.seed),
        str(protocol["scenarios"][record.scenario]),
        "10",
        "100000",
        "100",
        str(directory / "observations.csv"),
        "830",
        "1",
        str(directory / "traits.csv"),
    ]
    with (directory / "aggregate.csv").open() as f:
        rows = list(csv.DictReader(f))
    assert len(rows) == record.observations
    cycles = [int(row["cycle"]) for row in rows]
    assert cycles == sorted(
        {1, record.final_cycle, *range(100, record.final_cycle + 1, 100)}
    )
    assert int(rows[-1]["population"]) == record.final_population
    assert record.final_cycle == 100000 or record.final_population == 0
    populations = {0: 830}
    for row in rows:
        assert all(math.isfinite(float(v)) for v in row.values())
        for key, value in row.items():
            if key not in ["mean_age", "gini"]:
                assert int(value) >= 0
        assert 0 <= float(row["gini"]) <= 1
        assert float(row["mean_age"]) >= 0
        assert int(row["conservation_error"]) == 0
        assert int(row["population"]) <= 2500 and int(row["landscape"]) <= 10000
        populations[int(row["cycle"])] = int(row["population"])
    counts = Counter()
    optimal = Counter()
    initial_ids = set()
    seen_joint = set()
    with (directory / "traits.csv").open() as f:
        for row in csv.DictReader(f):
            cycle, count, fertility, cost = (
                int(row[k]) for k in ["cycle", "count", "infertility", "birth_cost"]
            )
            step = protocol["scenarios"][record.scenario]
            assert fertility in range(step, 11 * step, step) and cost in range(
                0, 91, 10
            )
            assert count > 0 and cycle in populations
            if row["kind"] == "initial":
                identity = int(row["id"])
                assert cycle == 0 and count == 1 and identity not in initial_ids
                initial_ids.add(identity)
            else:
                assert row["kind"] == "joint" and row["id"] == row["parent_id"] == "-1"
                assert (cycle, fertility, cost) not in seen_joint
                seen_joint.add((cycle, fertility, cost))
                counts[cycle] += count
                if fertility == step and cost == 0:
                    optimal[cycle] += count
    assert initial_ids == set(range(830))
    assert all(counts[cycle] == population for cycle, population in populations.items())
    result = {
        "scenario": record.scenario,
        "seed": record.seed,
        "final_cycle": record.final_cycle,
        "observations": record.observations,
        "extinct": record.final_population == 0,
        "terminal_joint_optimum": optimal[record.final_cycle],
        "final_population": record.final_population,
    }
    if record.final_population == 0:
        result["windows"] = (
            "Undefined age/Gini after extinction; no survivor-only aggregate"
        )
    else:
        result["windows"] = {}
        for label, (start, stop) in zip(
            ["earlier", "later"], protocol["windows"], strict=True
        ):
            selected = [row for row in rows if start <= int(row["cycle"]) <= stop]
            assert len(selected) == (stop - start) // 100 + 1
            result["windows"][label] = {
                metric: math.fsum(float(row[metric]) for row in selected)
                / len(selected)
                for metric in metrics
            }
    per_seed.append(result)
report = {
    "validated_runs": len(records),
    "observations": sum(r.observations for r in records),
    "mode": "completed-prefix" if args.completed_prefix else "complete-ensemble",
    "protocol_sha256": hashlib.sha256(
        (root / "protocol.json").read_bytes()
    ).hexdigest(),
    "ledger_snapshot_sha256": hashlib.sha256(ledger).hexdigest(),
    "per_seed": per_seed,
    "statistics": {},
    "interpretation": "Conditional reconstruction. Seeds are independent units; no original sampling-window equivalence or paper acceptance criterion.",
}
if not args.completed_prefix:
    for scenario in ["stable", "chaotic"]:
        selected = [r for r in per_seed if r["scenario"] == scenario]
        assert len(selected) == 100
        extinct = [r["seed"] for r in selected if r["extinct"]]
        if extinct:
            report["statistics"][scenario] = {
                "extinct_seeds": extinct,
                "status": "Withheld: no extinct society is silently excluded",
            }
            continue
        estimates = {}
        for metric in metrics:
            a = np.array([r["windows"]["earlier"][metric] for r in selected])
            b = np.array([r["windows"]["later"][metric] for r in selected])
            estimates[metric] = {}
            for label, values in [
                ("earlier", a),
                ("later", b),
                ("paired_change", b - a),
            ]:
                mean = float(values.mean())
                sd = float(values.std(ddof=1))
                half = float(t.ppf(0.975, 99)) * sd / 10
                estimates[metric][label] = {
                    "mean": mean,
                    "sd": sd,
                    "ci95": [mean - half, mean + half],
                }
        report["statistics"][scenario] = {"extinct_seeds": [], "estimates": estimates}
args.output.mkdir(parents=True, exist_ok=False)
(args.output / "analysis.json").write_text(
    json.dumps(report, indent=2, allow_nan=False) + "\n"
)
(args.output / "completed-snapshot.jsonl").write_bytes(ledger)
print(json.dumps({k: report[k] for k in ["validated_runs", "observations", "mode"]}))
