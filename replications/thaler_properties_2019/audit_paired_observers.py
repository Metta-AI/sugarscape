"""Audit complete native trade/inheritance pairs; prefixes never emit inference."""

import argparse
import csv
import gzip
import hashlib
import io
import json
import math
from pathlib import Path

import numpy as np
from scipy import stats


def csv_rows(folder, kind):
    data = gzip.decompress((folder / f"trajectory.{kind}.csv.gz").read_bytes())
    return list(csv.DictReader(io.StringIO(data.decode())))


def gini(values):
    values = np.sort(np.asarray(values, dtype=float))
    assert np.isfinite(values).all()
    if len(values) == 0 or values.sum() <= 0 or (values < 0).any():
        return None
    ranks = np.arange(1, len(values) + 1)
    value = float(
        2 * np.dot(ranks, values) / (len(values) * values.sum())
        - (len(values) + 1) / len(values)
    )
    # A second formula checks extraction and normalization on every snapshot.
    alternative = float(
        sum(np.sum(values[i] - values[:i]) for i in range(len(values)))
        / (len(values) * values.sum())
    )
    assert math.isclose(value, alternative, abs_tol=1e-12)
    return value


parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("protocol", type=Path)
parser.add_argument(
    "native",
    type=Path,
    help="Observer directory containing source/, Observe.hs and observe",
)
parser.add_argument("output", type=Path)
parser.add_argument("runs", nargs="+", type=Path)
parser.add_argument("--allow-prefix", action="store_true")
parser.add_argument(
    "--reuse-control",
    nargs="+",
    type=Path,
    default=[],
    help="Pinned control protocol followed by existing control run directories",
)
args = parser.parse_args()
assert not args.output.exists()
protocol = json.loads(args.protocol.read_text())
assert len(protocol["variants"]) == 1
variant_key = next(iter(protocol["variants"]))
assert variant_key in ["original", "corrected"]
variant = protocol["variants"][variant_key]
assert (
    protocol["replications"]
    == len(protocol["seeds"])
    == len(set(protocol["seeds"]))
    == 100
)
for name, digest in variant["source_sha256"].items():
    assert (
        hashlib.sha256((args.native / "source" / name).read_bytes()).hexdigest()
        == digest
    )
assert (
    hashlib.sha256((args.native / "observe").read_bytes()).hexdigest()
    == variant["binary_sha256"]
)
assert (
    hashlib.sha256((args.native / "Observe.hs").read_bytes()).hexdigest()
    == variant["observer_sha256"]
)
scenarios = protocol["scenarios"]
inputs = [(root, protocol) for root in args.runs]
if args.reuse_control:
    assert variant_key == "corrected" and len(args.reuse_control) >= 2
    control_path, *control_roots = args.reuse_control
    control = json.loads(control_path.read_text())
    reuse = protocol["reused_control"]
    assert (
        hashlib.sha256(control_path.read_bytes()).hexdigest()
        == reuse["protocol_sha256"]
    )
    assert control["seeds"] == protocol["seeds"]
    assert control["replications"] == protocol["replications"]
    assert control["variants"] == protocol["variants"]
    assert reuse["scenario"] in control["scenarios"]
    assert [s["key"] for s in scenarios] == ["trade_on"]
    assert reuse["scenario"]["key"] == "trade_off"
    scenarios = [reuse["scenario"], *scenarios]
    inputs.extend((root, control) for root in control_roots)
keys = [scenario["key"] for scenario in scenarios]
assert keys in [["trade_off", "trade_on"], ["mating", "inheritance"]]
toggle = (
    "T rule active (trading):"
    if keys[0] == "trade_off"
    else "I rule active (inheritance):"
)
assert all(s["steps"] == 1000 and s["stride"] == 10 for s in scenarios)
records = {key: {} for key in keys}
reserved = set()
ledgers = []
ledger_bytes = []
for root, input_protocol in inputs:
    manifest = json.loads((root / "manifest.json").read_text())
    assert manifest["protocol"] == input_protocol and manifest["variant"] == variant_key
    assert (
        hashlib.sha256((root / "run_observer_ensemble.py").read_bytes()).hexdigest()
        == manifest["runner_sha256"]
    )
    start, stop = manifest["interval"]
    assert 0 <= start < stop <= 100
    input_keys = [s["key"] for s in input_protocol["scenarios"]]
    indices = {(key, index) for key in input_keys for index in range(start, stop)}
    assert not reserved.intersection(indices), "Overlapping execution intervals"
    reserved.update(indices)
    raw = (root / "completed.jsonl").read_bytes()
    assert raw.endswith(b"\n"), "Retry after the worker finishes its ledger append"
    ledger_bytes.append(raw)
    ledger = [json.loads(line) for line in raw.splitlines()]
    expected = [(key, index) for key in input_keys for index in range(start, stop)]
    assert [(r["scenario"], r["index"]) for r in ledger] == expected[: len(ledger)]
    assert len(ledger) <= len(expected)
    if not args.allow_prefix:
        assert len(ledger) == len(expected), (
            "Incomplete ledger cannot support ensemble inference"
        )
        assert json.loads((root / "complete.json").read_text()) == {
            "completed_runs": len(expected)
        }
    ledgers.append(
        {
            "root": str(root),
            "sha256": hashlib.sha256(raw).hexdigest(),
            "records": len(ledger),
        }
    )
    for record in ledger:
        assert record["variant"] == variant_key
        assert record["seed"] == protocol["seeds"][record["index"]]
        assert record["steps"] == 1000 and record["summary_rows"] == 1001
        if record["scenario"] in keys:
            records[record["scenario"]][record["index"]] = (root, record)
paired = sorted(set(records[keys[0]]).intersection(records[keys[1]]))
if not args.allow_prefix:
    assert paired == list(range(100)), "All 100 pairs required"
assert paired, "No complete pairs available"
results = []
for index in paired:
    initial = []
    texts = []
    measurements = {}
    for scenario in scenarios:
        key = scenario["key"]
        root, record = records[key][index]
        folder = root / key / f"{index:03d}-{record['seed']}"
        assert json.loads((folder / "exit.json").read_text()) == {"exit_code": 0}
        for name, digest in record["files_sha256"].items():
            if name.endswith(".csv"):
                data = gzip.decompress((folder / (name + ".gz")).read_bytes())
            else:
                data = (folder / name).read_bytes()
            assert hashlib.sha256(data).hexdigest() == digest, str(folder / name)
        command = json.loads((folder / "command.json").read_text())
        assert len(command) == 6 and command[:5] == [
            variant["root"] + "/observe",
            scenario["constructor"],
            str(record["seed"]),
            "1000",
            "10",
        ]
        assert command[-1].endswith(f"/{key}/{index:03d}-{record['seed']}/trajectory")
        summaries = csv_rows(folder, "summary")
        assert [int(row["time"]) for row in summaries] == list(range(1001))
        assert all(
            math.isfinite(float(value)) for row in summaries for value in row.values()
        )
        agents = {t: [] for t in range(0, 1001, 10)}
        trades = {t: [] for t in agents}
        for row in csv_rows(folder, "agents"):
            assert all(
                math.isfinite(float(value))
                for field, value in row.items()
                if field != "culture"
            )
            agents[int(row["time"])].append(row)
        for row in csv_rows(folder, "trades"):
            assert all(math.isfinite(float(value)) for value in row.values())
            trades[int(row["time"])].append(row)
        for time, group in agents.items():
            assert (
                len(group)
                == len({row["id"] for row in group})
                == int(summaries[time]["population"])
            )
            assert len(trades[time]) == int(summaries[time]["trade_count"])
            for field in ["sugar", "spice"]:
                assert math.isclose(
                    sum(float(row[field]) for row in group),
                    float(summaries[time]["agent_" + field]),
                    rel_tol=1e-12,
                    abs_tol=1e-9,
                )
        cells = csv_rows(folder, "cells")
        assert set(int(row["time"]) for row in cells) == {0, 1000}
        initial.append(
            {
                "agents": agents[0],
                "cells": [r for r in cells if r["time"] == "0"],
                "summary": summaries[0],
            }
        )
        texts.append((folder / "trajectory.scenario.txt").read_text().splitlines())
        final = agents[1000]
        assert len(final) == record["final_population"]
        metrics = {
            "final_population": len(final),
            "late_population": float(
                np.mean([int(r["population"]) for r in summaries[801:]])
            ),
            "final_sugar_gini": gini([float(r["sugar"]) for r in final]),
        }
        if key in ["trade_off", "trade_on"]:
            for field in ["vision", "sugar_metabolism", "spice_metabolism"]:
                metrics["final_" + field] = (
                    float(np.mean([float(r[field]) for r in final])) if final else None
                )
            metrics["final_combined_wealth_gini"] = gini(
                [float(r["sugar"]) + float(r["spice"]) for r in final]
            )
        else:
            late_ginis = [
                gini([float(r["sugar"]) for r in agents[t]])
                for t in range(810, 1001, 10)
            ]
            metrics["late_sugar_gini"] = (
                float(np.mean(late_ginis))
                if all(v is not None for v in late_ginis)
                else None
            )
        measurements[key] = {
            "metrics": metrics,
            "snapshot_agent_observations": sum(map(len, agents.values())),
            "snapshot_trade_records": sum(map(len, trades.values())),
            "extinction_times": [
                int(r["time"]) for r in summaries if int(r["population"]) == 0
            ],
            "population_trajectory": [int(r["population"]) for r in summaries],
        }
    assert initial[0] == initial[1], "Paired initial conditions differ"
    assert len(texts[0]) == len(texts[1])
    differences = [(a, b) for a, b in zip(*texts) if a != b]
    assert len(differences) == 3
    assert all(v.startswith("Constructor:") for v in differences[0])
    assert all(v.startswith("Scenario:") for v in differences[1])
    assert all(v.startswith(toggle) for v in differences[2])
    assert differences[2][0].endswith("False") and differences[2][1].endswith("True")
    results.append(
        {"index": index, "seed": protocol["seeds"][index], "scenarios": measurements}
    )
comparisons = []
if not args.allow_prefix:
    for metric in results[0]["scenarios"][keys[0]]["metrics"]:
        missing = [
            r["index"]
            for r in results
            if any(r["scenarios"][key]["metrics"][metric] is None for key in keys)
        ]
        if missing:
            comparisons.append(
                {
                    "metric": metric,
                    "status": "undefined",
                    "undefined_pair_indices": missing,
                }
            )
            continue
        arrays = [
            np.array([r["scenarios"][key]["metrics"][metric] for r in results])
            for key in keys
        ]
        estimates = {}
        for label, values in zip(
            [*keys, "paired_change"], [*arrays, arrays[1] - arrays[0]]
        ):
            assert np.isfinite(values).all()
            mean = float(values.mean())
            margin = float(stats.t.ppf(0.975, 99) * stats.sem(values))
            estimates[label] = {"mean": mean, "ci95": [mean - margin, mean + margin]}
        comparisons.append(
            {"metric": metric, "status": "defined", "n": 100, "estimates": estimates}
        )
sidecars = args.output.with_name(args.output.stem + "-ledgers")
sidecars.mkdir(exist_ok=False)
for index, raw in enumerate(ledger_bytes):
    snapshot = sidecars / f"{index:03d}.jsonl"
    snapshot.write_bytes(raw)
    ledgers[index]["snapshot"] = str(snapshot.relative_to(args.output.parent))
report = {
    "protocol_sha256": hashlib.sha256(args.protocol.read_bytes()).hexdigest(),
    "auditor_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    "ledgers": ledgers,
    "complete_ensemble": not args.allow_prefix,
    "validated_pairs": len(paired),
    "unpaired_records_not_audited": {
        key: sorted(set(records[key]) - set(paired)) for key in keys
    },
    "source_files_verified": len(variant["source_sha256"]),
    "initial_conditions_exact": True,
    "only_dynamics_difference": toggle,
    "results": results,
    "comparisons": comparisons,
    "scope": "Original-source paired trajectories. Prefix mode emits no inference. Undefined outcomes remain explicit; no complete-paper verdict.",
}
if args.reuse_control:
    report["variant"] = variant_key
    report["reused_control_protocol_sha256"] = reuse["protocol_sha256"]
    report["excluded_control_scenarios"] = [
        s["key"] for s in control["scenarios"] if s["key"] not in keys
    ]
    report["scope"] = (
        "Coordinate/observation-corrected paired trade sensitivity; reused controls. "
        "Only listed paired scenarios audited, not excluded control scenarios. "
        "Prefix mode emits no inference. No complete-paper verdict."
    )
with args.output.open("x") as stream:
    stream.write(json.dumps(report, indent=2, allow_nan=False) + "\n")
print(
    json.dumps(
        {
            "validated_pairs": len(paired),
            "complete_ensemble": report["complete_ensemble"],
            "comparisons": comparisons,
        }
    )
)
