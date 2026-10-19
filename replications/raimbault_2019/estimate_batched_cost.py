"""Compute an allocation envelope for weighted frozen-sample batch times, not a runtime guarantee."""

import argparse
from decimal import Decimal
import hashlib
import json
from pathlib import Path

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("sizing", type=Path)
parser.add_argument("batched", type=Path)
parser.add_argument("output", type=Path)
parser.add_argument("--node-hour-price", type=float, required=True)
args = parser.parse_args()
assert not args.output.exists() and 0 < args.node_hour_price < 100
sizing = json.loads(args.sizing.read_text())
batched = json.loads(args.batched.read_text())
rows = sizing["rows"]
assert sizing["completed_rows"] == batched["completed_inputs"] == len(rows) == 550
assert sizing["exact_measurements"] == batched["exact_measurements"] == 6600
assert sum(r["stratum_rows"] for r in rows) == 2727994
assert [r["selected_row"] for r in rows] == list(range(550))
assert len({(r["id"], r["population"]) for r in rows}) == 550
assert [b["interval"] for b in batched["batches"]] == [
    [i * 550 // 8, (i + 1) * 550 // 8] for i in range(8)
]
assert sum(Decimal(str(b["cpu_seconds"])) for b in batched["batches"]) == Decimal(
    str(batched["cpu_seconds"])
)
bounds = {"cpu_seconds": [0.0, 0.0], "wall_seconds": [0.0, 0.0]}
weights = []
for batch in batched["batches"]:
    first, stop = batch["interval"]
    w = [r["stratum_rows"] for r in rows[first:stop]]
    minimum, maximum = min(w), max(w)
    weights.append(
        {
            "interval": [first, stop],
            "minimum_stratum_rows": minimum,
            "maximum_stratum_rows": maximum,
        }
    )
    for metric in bounds:
        assert batch[metric] > 0
        bounds[metric][0] += minimum * batch[metric]
        bounds[metric][1] += maximum * batch[metric]
node_hours = [v / 3600 / 8 for v in bounds["wall_seconds"]]
report = {
    "source_sha256": {
        str(p): hashlib.sha256(p.read_bytes()).hexdigest()
        for p in [args.sizing, args.batched]
    },
    "formula": "For each batch, min(w)*T <= sum(w_i*t_i) <= max(w)*T for any t_i>=0 summing to observed batch time T. Sum batch bounds; do not infer individual t_i.",
    "batch_weights": weights,
    "weighted_sample_cpu_hours_envelope": [v / 3600 for v in bounds["cpu_seconds"]],
    "ideal_eight_worker_node_hours_scenario": node_hours,
    "node_hour_price_assumption": args.node_hour_price,
    "ideal_compute_cost_usd_scenario": [v * args.node_hour_price for v in node_hours],
    "eight_nodes_elapsed_days_scenario": [v / 8 / 24 for v in node_hours],
    "interpretation": "Allocation envelope for the frozen sample. Future ensemble costs are scenarios only, not statistical confidence bounds or guaranteed limits.",
    "assumptions": [
        "Allocate each observed batch total among its inputs as nonnegative times, including batch overhead.",
        "Extrapolate each sampled stratum input to every original run in that stratum; within-stratum timing variability is unmeasured.",
        "Assume comparable hardware and load, ideal balancing across eight workers per node, and no pricing change.",
        "Exclude setup, retries, transfer, storage, idle billing and queue delay. Includes the whole original grid, not just uncompleted inputs.",
        "Do not interpret the difference from separate-process measurements as a controlled speedup.",
    ],
    "new_simulations": 0,
}
args.output.write_text(json.dumps(report, indent=2) + "\n")
print(
    json.dumps(
        {
            k: report[k]
            for k in [
                "ideal_eight_worker_node_hours_scenario",
                "ideal_compute_cost_usd_scenario",
                "eight_nodes_elapsed_days_scenario",
            ]
        }
    )
)
