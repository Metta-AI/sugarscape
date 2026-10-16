"""Audit parameterized Phase III movement records and reconstruct every defined price measurement."""

import argparse
import ast
import csv
import hashlib
import json
import math
import statistics
import sys
from collections import defaultdict
from pathlib import Path

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
assert 0 <= args.start_index < 1200
assert sys.version_info[:2] == (3, 11), "Pinned AST audit requires Python 3.11"
assert not args.output.exists()
manifest_bytes = (args.run / "manifest.json").read_bytes()
manifest = json.loads(manifest_bytes)
assert manifest["required_runs"] == 1200 and manifest["steps"] == 1000
assert manifest["seeds"] == list(range(100)) and manifest["policy"] == "movement"
assert manifest["approaches"] == ["explicit", "network"]
assert manifest["thresholds"] == [1, 5, 10]
assert set(manifest["source_sha256"]) == {
    "run.py",
    "run_groups.py",
    "run_phase3_movement.py",
    "PHASE3_MOVEMENT_PROTOCOL.md",
    "run_high_focus.py",
    "correct_high_focus.py",
}
for name, digest in manifest["source_sha256"].items():
    assert hashlib.sha256((args.run / name).read_bytes()).hexdigest() == digest
ledger = (args.run / "completed.jsonl").read_bytes()
records = [json.loads(line) for line in ledger.splitlines()]
assert manifest["selectors"] == ["released", "corrected-highest"]
expected = [
    (seed, threshold, approach, selector)
    for seed in range(100)
    for threshold in [1, 5, 10]
    for approach in ["explicit", "network"]
    for selector in ["released", "corrected-highest"]
]
assert [
    (r["seed"], r["threshold"], r["approach"], r["selector"]) for r in records
] == expected[args.start_index : args.start_index + len(records)]
assert 0 < len(records) <= 1200 - args.start_index
if args.mode == "complete":
    assert args.start_index == 0, "Full-ensemble validation starts at ordinal zero"
    assert len(records) == 1200, "All 1200 declared runs are required"
    assert json.loads((args.run / "complete.json").read_text()) == {
        "completed_runs": 1200
    }
measurements = []
summaries = []
health_count = 0
for record in records:
    seed, threshold, approach = record["seed"], record["threshold"], record["approach"]
    variant = "groups-network" if approach == "network" else "policy-explicit"
    selector = record["selector"]
    stem = f"{approach}-{threshold}-{seed}-{selector}"
    target = args.run / stem
    configured = target if selector == "released" else target / "configured"
    run = configured / "run"
    assert record["exit_code"] == 0
    assert json.loads((args.run / (stem + ".exit.json")).read_text()) == {
        "exit_code": 0
    }
    expected_files = {
        "configuration.json",
        "parameterization-complete.json",
    } | {
        "run/" + name
        for name in [
            "manifest.json",
            "initial-agents.json",
            "prices.json",
            "population.csv",
            "observations.json",
            "health.csv",
            "complete.json",
            "exit.json",
        ]
    }
    if selector == "corrected-highest":
        expected_files = {"configured/" + name for name in expected_files} | {
            "correction.json",
            "original-step-high.py",
            "corrected-step-high.py",
        }
        correction = json.loads((target / "correction.json").read_text())
        assert (
            correction["module_sha256"]
            == manifest["source_sha256"]["correct_high_focus.py"]
        )
        assert (
            correction["runner_sha256"]
            == manifest["source_sha256"]["run_high_focus.py"]
        )
        original = ast.parse((target / "original-step-high.py").read_text())
        corrected = ast.parse((target / "corrected-step-high.py").read_text())
        reference = json.loads(
            Path(__file__).with_name("high_focus_source.json").read_text()
        )["methods"][approach]
        assert (
            hashlib.sha256(
                ast.dump(original.body[0], include_attributes=False).encode()
            ).hexdigest()
            == reference["original_ast_sha256"]
        ), "Original high-focus method differs from pinned source"
        changed = 0
        for node in ast.walk(original):
            if (
                isinstance(node, ast.Compare)
                and ast.unparse(node) == "max(highest) > max(new)"
            ):
                node.ops = [ast.Lt()]
                changed += 1
        assert changed == 1 and ast.dump(original) == ast.dump(corrected), (
            "Correction differs from the one declared operator change"
        )
    assert set(record["sha256"]) == expected_files
    suffix = [
        approach,
        str(threshold),
        *(["movement"] if selector == "released" else []),
        str(seed),
        str(recorded_root / stem),
    ]
    assert record["command"][-len(suffix) :] == suffix
    script = "run_groups.py" if selector == "released" else "run_high_focus.py"
    assert record["command"][1] == str(recorded_root / script)
    for name, digest in record["sha256"].items():
        assert hashlib.sha256((target / name).read_bytes()).hexdigest() == digest
    config = json.loads((configured / "configuration.json").read_text())
    assert [
        config[key] for key in ["approach", "threshold", "policy", "seed", "steps"]
    ] == [approach, threshold, "movement", seed, 1000], (
        "Configuration differs from declared condition"
    )
    assert config["source_sha256"] == manifest["source_sha256"]["run_groups.py"]
    assert json.loads((configured / "parameterization-complete.json").read_text()) == {
        "grouping_calls": 1000
    }
    metadata = json.loads((run / "manifest.json").read_text())
    assert (
        metadata["variant"],
        metadata["numpy_seed"],
        metadata["mesa_seed"],
        metadata["steps"],
    ) == (variant, seed, 42, 1000)
    assert metadata["revision"] == "585e53398f4f58e89ec184c83bb20819f0e4c96a"
    assert metadata["library_revision"] == "99d2091721076df9fff32e8b49a0e33e98c34a6f"
    source_hashes = json.loads(
        Path(__file__).with_name("phase23_source_hashes.json").read_text()
    )["examples"]["sha256"]
    directory = "Policy-Network" if approach == "network" else "Policy-Explicit"
    for path, digest in source_hashes.items():
        if path.startswith(directory + "/"):
            assert metadata["source_hashes"][Path(path).name] == digest
    assert metadata["runner_sha256"] == manifest["source_sha256"]["run.py"]
    assert [metadata[k] for k in ["python", "mesa", "numpy", "networkx"]] == [
        "3.11.14",
        "0.8.5",
        "1.26.4",
        "3.6.1",
    ]
    assert metadata["pythonhashseed"] == "0" and metadata["policy_random_seed"] == seed
    completion = json.loads((run / "complete.json").read_text())
    assert completion == record["completion"] and completion["steps"] == 1000
    rows = json.loads((run / "observations.json").read_text())
    assert [r["step"] for r in rows] == list(range(1, 1001))
    initial = json.loads((run / "initial-agents.json").read_text())
    previous = {r["id"] for r in initial}
    assert len(previous) == len(initial) == 200
    health = defaultdict(set)
    with (run / "health.csv").open() as stream:
        for r in csv.DictReader(stream):
            step, agent = int(r["Step"]), int(r["Agent"])
            assert 1 <= step <= 1000 and agent not in health[step]
            health[step].add(agent)
            health_count += 1
            assert all(
                math.isfinite(float(r[k])) for k in ["Sugar_Level", "Spice_Level"]
            )
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
        values = prices[str(step)] if str(step) in prices else []  # noqa: SIM401 -- Missing trades are an explicit observation state.
        assert all(math.isfinite(p) and p > 0 for p in values)
        logs = [math.log(p) for p in values]
        measurement = {
            "approach": approach,
            "selector": selector,
            "threshold": threshold,
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
            "approach": approach,
            "selector": selector,
            "threshold": threshold,
            "numpy_seed": seed,
            "final_individual_agents": len(previous),
            "extinct": len(previous) == 0,
            "price_steps": len(prices),
            "undefined_dispersion_steps": sum(r["trades"] < 2 for r in per_run),
            "windows": windows,
        }
    )
report = {
    "mode": args.mode,
    "validated_runs": len(records),
    "ordinal_interval": [args.start_index, args.start_index + len(records)],
    "recorded_root": str(recorded_root),
    "complete_ensemble": len(records) == 1200,
    "health_records": health_count,
    "price_step_records": len(measurements),
    "runs": summaries,
    "manifest_sha256": hashlib.sha256(manifest_bytes).hexdigest(),
    "ledger_sha256": hashlib.sha256(ledger).hexdigest(),
    "analyzer_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    "scope": "Source and raw-file integrity, identities, health reconciliation and native-notebook price definitions. Undefined prices/dispersion remain missing. No aggregate equivalence or paper verdict.",
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
    f"Validated {len(records)}/1200 runs, {health_count} health records and {len(measurements)} price-step records"
)
