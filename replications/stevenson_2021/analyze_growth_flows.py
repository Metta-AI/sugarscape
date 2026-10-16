"""Compare observed births and deaths with fitted logistic growth, without refitting."""

import argparse
import csv
import hashlib
import io
import json
from pathlib import Path

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("run", type=Path)
parser.add_argument("output", type=Path)
parser.add_argument("source", type=Path, help="Simulator source used by the saved run")
args = parser.parse_args()
manifest = json.loads((args.run / "manifest.json").read_text())
assert manifest["cycles"] == 3000 and manifest["record_every"] == 1
assert manifest["seeds"] == list(range(1, 101))
assert manifest["scenarios"] == {"low-fertility": [85, 0], "birth-cost": [10, 40]}
assert hashlib.sha256(args.source.read_bytes()).hexdigest() == manifest["source_sha256"]
records = [
    json.loads(line) for line in (args.run / "completed.jsonl").read_text().splitlines()
]
assert [(r["scenario"], r["seed"]) for r in records] == [
    (scenario, seed) for scenario in manifest["scenarios"] for seed in manifest["seeds"]
]
bands = [(1, 10), (11, 100), (101, 400), (401, 700), (701, 2500)]
seed_results = []
observations = 0
for record in records:
    name = f"{record['scenario']}-{record['seed']}.csv"
    raw = (args.run / name).read_bytes()
    assert hashlib.sha256(raw).hexdigest() == record["trajectory_sha256"]
    rows = list(csv.DictReader(io.StringIO(raw.decode())))
    assert len(rows) == 3000
    counters = [
        {"cycles": 0, "agent_cycles": 0, "births": 0, "deaths": 0} for _ in bands
    ]
    previous = 1
    for cycle, row in enumerate(rows, 1):
        assert int(row["cycle"]) == cycle
        population, births, deaths = (
            int(row[n]) for n in ["population", "births", "deaths"]
        )
        assert population == previous + births - deaths
        assert 0 <= births <= previous and 0 <= deaths <= previous
        assert int(row["conservation_error"]) == 0
        band = next(i for i, (low, high) in enumerate(bands) if low <= previous <= high)
        counter = counters[band]
        counter["cycles"] += 1
        counter["agent_cycles"] += previous
        counter["births"] += births
        counter["deaths"] += deaths
        previous = population
    observations += len(rows)
    for (low, high), counter in zip(bands, counters):
        seed_results.append(
            {
                "scenario": record["scenario"],
                "seed": record["seed"],
                "population_low": low,
                "population_high": high,
                **counter,
            }
        )
summaries = []
for scenario, (infertility, birth_cost) in manifest["scenarios"].items():
    for low, high in bands:
        selected = [
            r
            for r in seed_results
            if r["scenario"] == scenario and r["population_low"] == low
        ]
        totals = {
            key: sum(r[key] for r in selected)
            for key in ["cycles", "agent_cycles", "births", "deaths"]
        }
        exposure = totals["agent_cycles"]
        assert exposure > 0
        summaries.append(
            {
                "scenario": scenario,
                "population_low": low,
                "population_high": high,
                "infertility": infertility,
                "birth_cost": birth_cost,
                **totals,
                "births_per_agent_cycle": totals["births"] / exposure,
                "deaths_per_agent_cycle": totals["deaths"] / exposure,
                "net_growth_per_agent_cycle": (totals["births"] - totals["deaths"])
                / exposure,
                "fertility_draw_probability": 1 / infertility,
            }
        )
args.output.mkdir(parents=True, exist_ok=False)
with (args.output / "seed-bands.csv").open("x", newline="") as stream:
    writer = csv.DictWriter(stream, fieldnames=list(seed_results[0]))
    writer.writeheader()
    writer.writerows(seed_results)
report = {
    "observations": observations,
    "runs": len(records),
    "bands_use": "Population before the cycle; all visits retained, including revisits after declines.",
    "summary": summaries,
    "manifest_sha256": hashlib.sha256(
        (args.run / "manifest.json").read_bytes()
    ).hexdigest(),
    "scope": "Exploratory descriptive reanalysis of existing ensembles. Births per agent-cycle are not logistic-fit r. No new simulations, fitted author protocol, or paper replication verdict.",
}
(args.output / "analysis.json").write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps(report))
