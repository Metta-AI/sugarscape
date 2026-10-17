"""Inspect complete saved disease configurations without interpreting tuple comments as behavior."""

import argparse
import ast
import hashlib
import json
from pathlib import Path

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("cohort", type=Path)
parser.add_argument("protocol", type=Path)
parser.add_argument("output", type=Path)
args = parser.parse_args()
protocol = json.loads(args.protocol.read_text())
assert len(protocol["seeds"]) == len(set(protocol["seeds"])) == 100
rows = []
for scenario in ["disease_clear", "disease_persist"]:
    for index, seed in enumerate(protocol["seeds"]):
        configurations = []
        for variant in ["original", "corrected"]:
            path = (
                args.cohort
                / variant
                / scenario
                / f"{index:03d}-{seed}"
                / "trajectory.scenario.txt"
            )
            lines = path.read_text().splitlines()
            line = next(
                line for line in lines if line.startswith("E rule active (disease):")
            )
            fields = ast.literal_eval(line.split("Just ", 1)[1])
            immune, maximum_length, count, initial, pool = fields
            assert immune == 50 and count == len(pool) == 10
            assert maximum_length == (10 if scenario == "disease_clear" else 25)
            assert initial == (4 if scenario == "disease_clear" else 10)
            assert all(1 <= len(disease) <= maximum_length for disease in pool)
            configurations.append(fields)
            rows.append(
                {
                    "scenario": scenario,
                    "variant": variant,
                    "index": index,
                    "seed": seed,
                    "immune_length": immune,
                    "maximum_disease_length": maximum_length,
                    "disease_entries": len(pool),
                    "distinct_diseases": len(set(map(tuple, pool))),
                    "initial_diseases_per_agent": initial,
                    "lengths": list(map(len, pool)),
                    "configuration_sha256": hashlib.sha256(
                        path.read_bytes()
                    ).hexdigest(),
                }
            )
        assert configurations[0] == configurations[1]
report = {
    "rows": rows,
    "protocol_sha256": hashlib.sha256(args.protocol.read_bytes()).hexdigest(),
    "scope": "Observed resolved configurations only. Tuple positions describe generator behavior, which conflicts with the declared field order. Generated entries need not be distinct.",
}
with args.output.open("x") as stream:
    stream.write(json.dumps(report, indent=2, allow_nan=False) + "\n")
print(json.dumps({"verified_configurations": len(rows), "generated_disease_count": 10}))
