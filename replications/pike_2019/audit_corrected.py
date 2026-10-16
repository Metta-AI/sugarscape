"""Audit complete corrective runs without treating accounting as economic validity."""

import argparse
import csv
import hashlib
import json
import math
from collections import defaultdict
from pathlib import Path

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("run", type=Path)
parser.add_argument("output", type=Path)
args = parser.parse_args()
manifest = json.loads((args.run / "manifest.json").read_text())
complete = json.loads((args.run / "complete.json").read_text())
assert manifest["steps"] == complete["steps"] == 1000
rows = list(csv.DictReader((args.run / "accounting.csv").open()))
assert len(rows) == 2000
errors, population, previous = [], {}, {}
for index, row in enumerate(rows):
    step, commodity = int(row["step"]), row["commodity"]
    assert step == index // 2 + 1 and commodity == ["sugar", "spice"][index % 2]
    values = {
        key: float(row[key])
        for key in ["before", "after", "growth", "metabolism", "death_loss", "error"]
    }
    assert all(math.isfinite(value) for value in values.values())
    error = (
        values["after"]
        - values["before"]
        - values["growth"]
        + values["metabolism"]
        + values["death_loss"]
    )
    assert abs(error) < 1e-7 and abs(error - values["error"]) < 1e-10
    if step > 1:
        assert values["before"] == previous[commodity]
    previous[commodity] = values["after"]
    errors.append(abs(error))
    if commodity == "sugar":
        population[step] = int(row["population"])
    else:
        assert int(row["population"]) == population[step]
assert population[1000] == complete["individual_agents"]
health = list(csv.DictReader((args.run / "health.csv").open()))
identities = defaultdict(set)
negative = 0
for row in health:
    step, agent = int(row["Step"]), int(row["Agent"])
    assert 1 <= step <= 1000 and 0 <= agent < 200
    assert agent not in identities[step]
    identities[step].add(agent)
    values = [float(row[key]) for key in ["Sugar_Level", "Spice_Level"]]
    assert all(math.isfinite(value) for value in values)
    negative += min(values) < 0
for step in range(1, 1001):
    assert len(identities[step]) == population[step]
    if step > 1:
        assert identities[step] <= identities[step - 1]
prices = json.loads((args.run / "prices.json").read_text())
assert all(1 <= int(step) <= 1000 for step in prices)
assert all(
    math.isfinite(value) and value > 0 for values in prices.values() for value in values
)
summary = {
    "variant": manifest["variant"],
    "seed": manifest["numpy_seed"],
    "completed_steps": 1000,
    "final_population": population[1000],
    "max_accounting_error": max(errors),
    "health_records": len(health),
    "negative_health_records": negative,
    "transactions": sum(len(values) for values in prices.values()),
    "sha256": {
        name: hashlib.sha256((args.run / name).read_bytes()).hexdigest()
        for name in [
            "manifest.json",
            "complete.json",
            "accounting.csv",
            "health.csv",
            "prices.json",
        ]
    },
    "scope": "Measurement audit only; negative holdings and death accounting require model interpretation. No paper verdict.",
}
args.output.mkdir(parents=True, exist_ok=False)
(args.output / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
print(json.dumps(summary, indent=2))
