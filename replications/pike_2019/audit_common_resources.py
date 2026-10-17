"""Audit native common-resource records, explicitly retaining failed numerical validity."""

import argparse
from collections import defaultdict
import csv
import hashlib
import json
import math
from pathlib import Path
import statistics

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("run", type=Path)
parser.add_argument("mode", choices=["prefix", "complete"])
parser.add_argument("output", type=Path)
parser.add_argument(
    "--start-index", type=int, default=0, help="First ordinal in the declared full grid"
)
parser.add_argument(
    "--recorded-root",
    type=Path,
    help="Original execution root when auditing relocated evidence",
)
args = parser.parse_args()
recorded_root = args.run if args.recorded_root is None else args.recorded_root
assert 0 <= args.start_index < 198
assert not args.output.exists()
manifest_bytes = (args.run / "manifest.json").read_bytes()
manifest = json.loads(manifest_bytes)
assert manifest["required_runs"] == 198 and manifest["steps"] == 1000
assert manifest["numpy_seeds"] == list(range(1, 100)) and manifest["mesa_seed"] == 42
assert manifest["variants"] == ["common-one", "common-multi"]
for name, digest in manifest["source_hashes"].items():
    assert hashlib.sha256((args.run / name).read_bytes()).hexdigest() == digest
ledger = (args.run / "completed.jsonl").read_bytes()
records = [json.loads(line) for line in ledger.splitlines()]
expected = [
    (seed, variant) for seed in range(1, 100) for variant in manifest["variants"]
]
assert [(r["numpy_seed"], r["variant"]) for r in records] == expected[
    args.start_index : args.start_index + len(records)
]
assert 0 < len(records) <= 198 - args.start_index
if args.mode == "complete":
    assert args.start_index == 0, "Full-ensemble validation starts at ordinal zero"
    assert len(records) == 198, "All 198 declared runs are required"
    assert json.loads((args.run / "complete.json").read_text()) == {
        "completed_runs": 198
    }
measurements = []
summaries = []
health_count = 0
for record in records:
    seed, variant = record["numpy_seed"], record["variant"]
    stem = f"{variant}-{seed}"
    run = args.run / stem
    assert record["exit_code"] == 0
    assert json.loads((args.run / (stem + ".exit.json")).read_text()) == {
        "exit_code": 0
    }
    assert set(record["hashes"]) == {
        "manifest.json",
        "initial-agents.json",
        "prices.json",
        "population.csv",
        "observations.json",
        "health.csv",
        "complete.json",
        "exit.json",
    }
    assert record["command"][-3:] == [variant, str(seed), str(recorded_root / stem)]
    for name, digest in record["hashes"].items():
        assert hashlib.sha256((run / name).read_bytes()).hexdigest() == digest
    metadata = json.loads((run / "manifest.json").read_text())
    assert (
        metadata["variant"],
        metadata["numpy_seed"],
        metadata["mesa_seed"],
        metadata["steps"],
    ) == (variant, seed, 42, 1000)
    assert metadata["revision"] == "585e53398f4f58e89ec184c83bb20819f0e4c96a"
    assert metadata["library_revision"] == "99d2091721076df9fff32e8b49a0e33e98c34a6f"
    assert metadata["pythonhashseed"] == "0" and metadata["policy_random_seed"] == seed
    assert metadata["runner_sha256"] == manifest["source_hashes"]["run.py"]
    assert [metadata[k] for k in ["python", "mesa", "numpy", "networkx"]] == [
        "3.11.14",
        "0.8.5",
        "1.26.4",
        "3.6.1",
    ]
    completion = json.loads((run / "complete.json").read_text())
    assert completion == record["completion"] and completion["steps"] == 1000
    rows = json.loads((run / "observations.json").read_text())
    assert [r["step"] for r in rows] == list(range(1, 1001))
    initial = json.loads((run / "initial-agents.json").read_text())
    previous = {r["id"] for r in initial}
    assert len(previous) == len(initial) == 200
    nonfinite_steps = []
    negative_records = 0
    health = defaultdict(set)
    with (run / "health.csv").open() as stream:
        for r in csv.DictReader(stream):
            step, agent = int(r["Step"]), int(r["Agent"])
            assert 1 <= step <= 1000 and agent not in health[step]
            health[step].add(agent)
            health_count += 1
            holdings = [float(r[k]) for k in ["Sugar_Level", "Spice_Level"]]
            if not all(math.isfinite(value) for value in holdings):
                nonfinite_steps.append(step)
            if any(value < 0 for value in holdings):
                negative_records += 1
    for r in rows:
        ids = set(r["agent_ids"])
        assert len(ids) == len(r["agent_ids"]) == r["individual_agents"]
        assert ids <= previous and ids == health[r["step"]]
        previous = ids
    assert completion["individual_agents"] == rows[-1]["individual_agents"]
    assert completion["native_reporter"] == rows[-1]["native_reporter"]
    prices = json.loads((run / "prices.json").read_text())
    assert all(str(int(k)) == k and 1 <= int(k) <= 1000 for k in prices)
    per_run = []
    for step in range(1, 1001):
        values = prices[str(step)] if str(step) in prices else []
        assert all(math.isfinite(p) and p > 0 for p in values)
        logs = [math.log(p) for p in values]
        measurement = {
            "variant": variant,
            "numpy_seed": seed,
            "step": step,
            "trades": len(values),
            "geometric_mean_price": math.exp(statistics.fmean(logs)) if logs else None,
            "sample_sd_log_price": statistics.stdev(logs) if len(logs) >= 2 else None,
        }
        measurements.append(measurement)
        per_run.append(measurement)
    windows = {}
    for label, start, stop in [("early", 1, 100), ("late", 901, 1000)]:
        selected = [r for r in per_run if start <= r["step"] <= stop]
        assert len(selected) == 100
        windows[label] = {"trades": sum(r["trades"] for r in selected)}
        for metric in ["geometric_mean_price", "sample_sd_log_price"]:
            defined = [r[metric] for r in selected if r[metric] is not None]
            windows[label][metric] = {
                "defined_steps": len(defined),
                "mean_over_defined_steps": statistics.fmean(defined)
                if defined
                else None,
            }
    summaries.append(
        {
            "variant": variant,
            "numpy_seed": seed,
            "final_individual_agents": len(previous),
            "extinct": len(previous) == 0,
            "nonfinite_health_records": len(nonfinite_steps),
            "first_nonfinite_step": min(nonfinite_steps) if nonfinite_steps else None,
            "negative_health_records": negative_records,
            "numeric_validation": "failed" if nonfinite_steps else "passed",
            "price_steps": len(prices),
            "undefined_dispersion_steps": sum(r["trades"] < 2 for r in per_run),
            "windows": windows,
        }
    )
report = {
    "mode": args.mode,
    "structurally_audited_runs": len(records),
    "numerically_failed_runs": sum(
        r["numeric_validation"] == "failed" for r in summaries
    ),
    "ordinal_interval": [args.start_index, args.start_index + len(records)],
    "recorded_root": str(recorded_root),
    "complete_new_seed_batch": len(records) == 198,
    "full_grid_includes_two_separate_seed_zero_runs": True,
    "health_records": health_count,
    "price_step_records": len(measurements),
    "runs": summaries,
    "manifest_sha256": hashlib.sha256(manifest_bytes).hexdigest(),
    "ledger_sha256": hashlib.sha256(ledger).hexdigest(),
    "analyzer_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    "scope": "Structural source/file/identity audit plus explicit numerical-failure diagnosis. Infinite holdings are retained and counted as failures, not converted into passing economic results. Price/dispersion remain undefined where mathematically undefined. The complete new-seed batch still requires two separately audited seed-zero runs. No paper verdict.",
}
args.output.mkdir(parents=True, exist_ok=False)
(args.output / "ledger-snapshot.jsonl").write_bytes(ledger)
(args.output / "audit.json").write_text(
    json.dumps(report, indent=2, allow_nan=False) + "\n"
)
with (args.output / "price-measurements.csv").open("x", newline="") as stream:
    writer = csv.DictWriter(stream, fieldnames=list(measurements[0]))
    writer.writeheader()
    writer.writerows(measurements)
print(
    f"Structurally audited {len(records)}/198 runs, {health_count} health records and {len(measurements)} price-step records"
)
