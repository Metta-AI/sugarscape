"""Audit the complete exploratory fixed-parameter seed ensemble; retain all runs."""

import argparse
import csv
import hashlib
import json
import math
import statistics
from pathlib import Path

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("run", type=Path)
parser.add_argument("output", type=Path)
args = parser.parse_args()
protocol = json.loads((args.run / "protocol.json").read_text())
complete = json.loads((args.run / "complete.json").read_text())
seeds = protocol["fresh_seeds"]
assert seeds == list(range(64))
for name, expected in protocol["input_sha256"].items():
    assert hashlib.sha256(Path(name).read_bytes()).hexdigest() == expected
with (args.run / "parameters.csv").open() as stream:
    parameters = list(csv.DictReader(stream))
assert len(parameters) == len(seeds)
for seed, row in zip(seeds, parameters):
    assert int(row["random-seed"]) == seed
    for name, value in protocol["original_parameters"].items():
        if name != "random-seed":
            assert row[name] == value
    independent_parameters = json.loads(
        (args.run / "independent-parameters" / f"{seed}.json").read_text()
    )
    assert independent_parameters == {
        "population": int(float(row["initial-population"])),
        "mutation": float(row["pmut"]),
        "maximum_sugar": int(float(row["maximum-sugar-endowment"])),
        "maximum_spice": int(float(row["maximum-spice-endowment"])),
        "reproduction": float(row["wealth-reproduction"]),
        "seed": seed,
    }
assert complete == {"native_runs": 64, "independent_runs": 64, "exit_code": 0}
receipts = [
    json.loads(line) for line in (args.run / "completed.jsonl").read_text().splitlines()
]
assert [r["name"] for r in receipts] == ["native"] + [f"independent-{s}" for s in seeds]
assert all(r["exit_code"] == 0 for r in receipts)
columns = {
    "native": [
        "tick",
        "count turtles",
        "normalized-gini",
        "sum [psugar] of patches",
        "sum [pspice] of patches",
        "number_of_prices",
        "mean_prices",
    ],
    "independent": [
        "tick",
        "population",
        "gini",
        "landscape_sugar",
        "landscape_spice",
        "trade_count",
        "mean_price",
    ],
}
records = []
hashes = {}
observations = 0
for variant, names in columns.items():
    for seed in seeds:
        path = args.run / variant / f"row-{seed}.csv"
        hashes[f"{variant}/row-{seed}.csv"] = hashlib.sha256(
            path.read_bytes()
        ).hexdigest()
        with path.open() as stream:
            reader = csv.DictReader(stream)
            assert reader.fieldnames == names
            rows = [[float(row[n]) for n in names] for row in reader]
        assert len(rows) == protocol["observations_per_run"] == 501
        assert rows[0][0] == 0 and rows[0][1] == float(
            protocol["original_parameters"]["initial-population"]
        )
        for index, row in enumerate(rows):
            assert all(math.isfinite(v) for v in row)
            tick, population, gini, sugar, spice, trades, price = row
            assert (
                tick == int(tick)
                and population == int(population)
                and trades == int(trades)
            )
            assert (
                population >= 0
                and trades >= 0
                and sugar >= 0
                and spice >= 0
                and price >= 0
            )
            assert -1e-12 <= gini <= 1 + 1e-12
            if index:
                prior = rows[index - 1]
                if prior[1] == 0:
                    assert row == prior
                else:
                    assert tick == prior[0] + 1
        observations += len(rows)
        prices = [r[6] for r in rows]
        records.append(
            {
                "variant": variant,
                "seed": seed,
                "observations": len(rows),
                "price_at450": rows[450][6],
                "price_at475": rows[475][6],
                "last_price": prices[-1],
                "maximum_price": max(prices),
                "mean_price": statistics.mean(prices),
                "last_population": rows[-1][1],
                "minimum_population": min(r[1] for r in rows),
                "extinct": rows[-1][1] == 0,
            }
        )
summary = []
for variant in columns:
    group = [r for r in records if r["variant"] == variant]
    for metric in [
        "price_at450",
        "price_at475",
        "last_price",
        "maximum_price",
        "mean_price",
        "last_population",
    ]:
        values = [r[metric] for r in group]
        summary.append(
            {
                "variant": variant,
                "metric": metric,
                "runs": len(values),
                "minimum": min(values),
                "median": statistics.median(values),
                "mean": statistics.mean(values),
                "maximum": max(values),
            }
        )
args.output.mkdir(exist_ok=False)
for filename, data in [("runs.csv", records), ("summary.csv", summary)]:
    with (args.output / filename).open("w") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(data[0]))
        writer.writeheader()
        writer.writerows(data)
(args.output / "audit.json").write_text(
    json.dumps(
        {
            "runs": len(records),
            "observations": observations,
            "excluded_runs": 0,
            "protocol_sha256": hashlib.sha256(
                (args.run / "protocol.json").read_bytes()
            ).hexdigest(),
            "trajectory_sha256": hashes,
            "scope": "Complete exploratory fixed-parameter runs with different random streams. All trajectories finite and follow observation/terminal-state accounting. Does not independently replay every state transition or establish distributional equivalence or a paper-level verdict.",
        },
        indent=2,
    )
    + "\n"
)
print(json.dumps({"runs": len(records), "observations": observations}))
