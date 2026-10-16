"""Independently audit sizing outputs; estimate full workload only from all strata."""

import argparse
import csv
import gzip
import hashlib
import json
import math
from pathlib import Path

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("run", type=Path)
parser.add_argument("output", type=Path)
parser.add_argument("--require-complete", action="store_true")
parser.add_argument("--hourly-node-price", type=float, required=True)
args = parser.parse_args()
assert math.isfinite(args.hourly_node_price) and args.hourly_node_price > 0
selection = json.loads((args.run / "selection.json").read_text())
assert (
    selection["original_sha256"]
    == "1a2cdf93167571ab2943d488017ace08945e7afd3cd8ac4d1410fb214c79c8f5"
)
assert (
    hashlib.sha256((args.run / "selection.json").read_bytes()).hexdigest()
    == "7a9728b755a9399d3631c642bec87c833cf9e78f3565bb91e27100802f88d66e"
)
assert (
    hashlib.sha256((args.run / "selected.csv.gz").read_bytes()).hexdigest()
    == selection["selected_gzip_sha256"]
)
with gzip.open(args.run / "selected.csv.gz", "rt") as stream:
    inputs = list(csv.DictReader(stream))
assert len(inputs) == selection["selected_rows"] == 550
assert len({(r["id"], r["population"]) for r in selection["rows"]}) == 550
assert (
    sum(r["stratum_rows"] for r in selection["rows"])
    == selection["original_rows"]
    == 2727994
)
start = json.loads((args.run / "start.json").read_text())
assert start["workers"] == 8
assert (
    start["runner_sha256"]
    == hashlib.sha256((args.run / "run.py").read_bytes()).hexdigest()
)
assert (
    start["selection_sha256"]
    == hashlib.sha256((args.run / "selection.json").read_bytes()).hexdigest()
)
assert start["source_sha256"] == json.loads(
    (args.run / "expected-runtime.json").read_text()
)
metrics = [
    "gini",
    "mwgini",
    "moran",
    "distance",
    "entropy",
    "slope",
    "rsquared",
    "moranRessource",
    "distanceRessource",
    "entropyRessource",
    "slopeRessource",
    "rsquaredRessource",
]
rows = []
exact = 0
maximum_error = 0.0
hashes = {}
for directory in sorted((args.run / "runs").glob("row-*")):
    index = int(directory.name.removeprefix("row-"))
    assert 0 <= index < 550
    assert directory.name == f"row-{index:04d}"
    ref = inputs[index]
    selected = selection["rows"][index]
    assert selected["selected_row"] == index
    assert selected["id"] == ref["id"] and selected["seed"] == ref["replication"]
    assert selected["population"] == float(ref["population"])
    status = json.loads((directory / "exit.json").read_text())
    assert status["exit_code"] == 0
    output = list(csv.DictReader((directory / "results.csv").open()))
    assert len(output) == 1
    actual = output[0]
    assert int(actual["row"]) == index and actual["id"] == ref["id"]
    assert actual["seed"] == ref["replication"]
    assert float(actual["population"]) == float(ref["population"])
    assert float(actual["ticks"]) == 10000
    for metric in metrics:
        value, target = float(actual[metric]), float(ref[metric])
        assert math.isfinite(value) and math.isfinite(target)
        error = abs(value - target)
        assert error <= (0 if metric in ("gini", "mwgini") else 1e-12), (
            index,
            metric,
            error,
        )
        exact += error == 0
        maximum_error = max(maximum_error, error)
    user, system, memory = map(float, (directory / "resources.txt").read_text().split())
    wall = status["elapsed_seconds"]
    assert all(math.isfinite(x) and x >= 0 for x in (user, system, memory, wall))
    assert user + system > 0 and wall > 0 and memory > 0
    rows.append(
        {
            **selected,
            "cpu_seconds": user + system,
            "wall_seconds": wall,
            "peak_rss_kib": memory,
        }
    )
    for name in ("results.csv", "exit.json", "resources.txt", "command.json"):
        path = directory / name
        hashes[str(path.relative_to(args.run))] = hashlib.sha256(
            path.read_bytes()
        ).hexdigest()
indices = [row["selected_row"] for row in rows]
assert len(indices) == len(set(indices)), "Duplicate selected inputs"
complete = indices == list(range(550))
if args.require_complete:
    assert complete, f"Full sizing requires all 550 strata; observed {len(rows)}"
report = {
    "completed_rows": len(rows),
    "complete": complete,
    "measurements": len(rows) * 12,
    "exact_measurements": exact,
    "maximum_error": maximum_error,
    "rows": rows,
    "artifact_sha256": hashes,
    "hourly_node_price_assumption": args.hourly_node_price,
    "scope": "Sizing sample; does not establish full generated-ensemble replication.",
}
if complete:
    cpu = sum(r["cpu_seconds"] * r["stratum_rows"] for r in rows)
    wall = sum(r["wall_seconds"] * r["stratum_rows"] for r in rows)
    report["projection"] = {
        "full_inputs": selection["original_rows"],
        "weighted_cpu_hours": cpu / 3600,
        "ideal_eight_cpu_node_hours": cpu / 3600 / 8,
        "eight_worker_elapsed_projection_hours": wall / 3600 / 8,
        "ideal_cpu_cost": cpu / 3600 / 8 * args.hourly_node_price,
        "elapsed_projection_cost": wall / 3600 / 8 * args.hourly_node_price,
        "assumptions": "Same workload, eight workers and performance; fixed supplied price. Includes per-input Java startup. Excludes setup, retries, idle time and transfer. One sample per stratum cannot estimate within-stratum variance; no confidence interval or guaranteed budget.",
    }
args.output.mkdir(parents=True, exist_ok=False)
(args.output / "analysis.json").write_text(json.dumps(report, indent=2) + "\n")
print(
    json.dumps(
        {k: v for k, v in report.items() if k not in ("rows", "artifact_sha256")}
    )
)
