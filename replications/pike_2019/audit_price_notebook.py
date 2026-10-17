"""Replay the author's plotted price definitions on complete audited ensembles."""

import argparse
import ast
from collections import defaultdict
import csv
import hashlib
import json
import math
from pathlib import Path
import statistics
import subprocess

import numpy as np
from scipy.stats.mstats import gmean

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("source", type=Path)
parser.add_argument("phase1", type=Path)
parser.add_argument("phase3", type=Path)
parser.add_argument("output", type=Path)
args = parser.parse_args()
revision = subprocess.check_output(
    ["git", "-C", str(args.source), "rev-parse", "HEAD"], text=True
).strip()
assert revision == "585e53398f4f58e89ec184c83bb20819f0e4c96a"
notebook_path = args.source / "Results Analysis Code/Data Analysis-Groups-Policy.ipynb"
relative_notebook = str(notebook_path.relative_to(args.source))
notebook_raw = notebook_path.read_bytes()
assert notebook_raw == subprocess.check_output(
    ["git", "-C", str(args.source), "show", f"HEAD:{relative_notebook}"]
)
notebook = json.loads(notebook_raw)
namespace = {
    "defaultdict": defaultdict,
    "log": math.log,
    "stdev": statistics.stdev,
    "gmean": gmean,
}
source_cells = {}
for index, name in [(2, "make_distro"), (7, "ind_price"), (15, "sdlm")]:
    source = "".join(notebook["cells"][index]["source"])
    source_cells[str(index)] = source
    functions = [
        node for node in ast.parse(source).body if isinstance(node, ast.FunctionDef)
    ]
    assert len(functions) == 1 and functions[0].name == name
    exec(
        compile(
            ast.Module(body=functions, type_ignores=[]), str(notebook_path), "exec"
        ),
        namespace,
    )
source_cells["17"] = "".join(notebook["cells"][17]["source"])
inputs = {str(notebook_path): hashlib.sha256(notebook_raw).hexdigest()}
rows = []
histograms = []
pooled = defaultdict(list)
counts = defaultdict(lambda: defaultdict(int))
seen = set()
max_error = 0.0
for directory, phase, required in [(args.phase1, 1, 300), (args.phase3, 3, 1200)]:
    report_path = directory / "reconciliation.json"
    raw = report_path.read_bytes()
    report = json.loads(raw)
    assert report["phase"] == phase and report["complete_grid"]
    assert report["validated_runs"] == report["required_runs"] == required
    assert report["missing_ordinals"] == []
    inputs[str(report_path)] = hashlib.sha256(raw).hexdigest()
    for segment in report["segments"]:
        root = Path(segment["run"])
        ledger = (root / "completed.jsonl").read_bytes()
        assert hashlib.sha256(ledger).hexdigest() == segment["ledger_sha256"]
        inputs[str(root / "completed.jsonl")] = segment["ledger_sha256"]
        for record in map(json.loads, ledger.splitlines()):
            if phase == 1:
                if record["variant"] != "standard":
                    continue
                variant, seed = "standard", record["numpy_seed"]
                relative, hashes = "prices.json", record["hashes"]
            else:
                if record["threshold"] != 10 or record["selector"] != "released":
                    continue
                variant, seed = record["approach"], record["seed"]
                relative, hashes = "run/prices.json", record["sha256"]
            assert (variant, seed) not in seen
            seen.add((variant, seed))
            path = root / Path(record["command"][-1]).name / relative
            raw = path.read_bytes()
            assert hashlib.sha256(raw).hexdigest() == hashes[relative]
            inputs[str(path)] = hashes[relative]
            prices = json.loads(raw)
            assert all(
                str(int(step)) == step and 1 <= int(step) <= 1000 for step in prices
            )
            assert all(math.isfinite(p) and p > 0 for ps in prices.values() for p in ps)
            distro = namespace["make_distro"]({"run": prices})
            x_dev, y_dev, x_all, y_all = namespace["sdlm"](prices)
            # The notebook calls gmean on empty lists. Preserve missingness while
            # avoiding runtime-dependent empty-sample warnings during replay.
            nonempty = {step: ps for step, ps in prices.items() if ps}
            x_price, y_price = namespace["ind_price"](nonempty)
            signed = {
                str(step): np.log(prices[str(step)] if str(step) in prices else [])
                for step in range(1, 1001)
            }
            eligible = [step for step, ps in prices.items() if len(ps) >= 2]
            expected_distro = [float(np.std(signed[step], ddof=1)) for step in eligible]
            expected_abs_sd = [
                float(np.std(np.abs(signed[step]), ddof=1)) for step in eligible
            ]
            expected_scatter = [
                abs(math.log(p)) for step in eligible for p in prices[step]
            ]
            assert x_dev == eligible
            assert x_all == [step for step in eligible for _ in prices[step]]
            assert y_all == expected_scatter
            for actual, expected in [
                (distro, expected_distro),
                (y_dev, expected_abs_sd),
                (y_price, [float(np.exp(np.mean(signed[s]))) for s in x_price]),
            ]:
                error = (
                    float(np.max(np.abs(np.asarray(actual) - expected)))
                    if len(actual)
                    else 0.0
                )
                max_error = max(max_error, error)
                assert np.allclose(actual, expected, rtol=1e-12, atol=1e-12)
            pooled[variant].extend(distro)
            counts[variant]["steps"] += 1000
            counts[variant]["histogram_steps"] += len(distro)
            counts[variant]["scatter_transactions"] += len(y_all)
            counts[variant]["omitted_single_trade_steps"] += sum(
                len(ps) == 1 for ps in prices.values()
            )
            counts[variant]["no_trade_steps"] += 1000 - sum(
                bool(ps) for ps in prices.values()
            )
            counts[variant]["sd_definitions_differ_steps"] += sum(
                not math.isclose(a, b, rel_tol=1e-12, abs_tol=1e-12)
                for a, b in zip(distro, y_dev, strict=True)
            )
            for window, steps in [("early", range(1, 101)), ("late", range(901, 1001))]:
                selected = [signed[str(step)] for step in steps]
                metrics = {
                    "abs_log_geometric_mean": [
                        abs(float(np.mean(v))) for v in selected if len(v)
                    ],
                    "mean_absolute_log_transaction": [
                        float(np.mean(np.abs(v))) for v in selected if len(v)
                    ],
                    "sample_sd_log_price": [
                        float(np.std(v, ddof=1)) for v in selected if len(v) >= 2
                    ],
                }
                for metric, values in metrics.items():
                    rows.append(
                        {
                            "variant": variant,
                            "seed": seed,
                            "window": window,
                            "metric": metric,
                            "defined_steps": len(values),
                            "mean_over_defined_steps": statistics.fmean(values)
                            if values
                            else None,
                        }
                    )
assert seen == {(v, s) for v in ["standard", "explicit", "network"] for s in range(100)}
for count in counts.values():
    assert (
        count["histogram_steps"]
        + count["omitted_single_trade_steps"]
        + count["no_trade_steps"]
        == count["steps"]
    )
for variant, values in sorted(pooled.items()):
    bins, edges = np.histogram(values, bins=500)
    assert int(bins.sum()) == len(values)
    histograms.extend(
        {
            "variant": variant,
            "left": float(edges[i]),
            "right": float(edges[i + 1]),
            "count": int(count),
        }
        for i, count in enumerate(bins)
    )
args.output.mkdir(parents=True, exist_ok=False)
for filename, records in [
    ("run-measurements.csv", rows),
    ("histograms.csv", histograms),
]:
    with (args.output / filename).open("x") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(records[0]))
        writer.writeheader()
        writer.writerows(records)
result = {
    "source_revision": revision,
    "input_sha256": inputs,
    "source_cells": source_cells,
    "runs": len(seen),
    "counts": counts,
    "max_definition_error": max_error,
    "scope": "Complete standard PhaseI100 and released movement threshold10 explicit/network100each. Native notebook histogram is sampleSD(log(price)); its scatter is abs(log(price)) only for steps with>=2trades, NOT the computed sampleSD(abs(log(price))). Replay excludes empty inputs to ind_price and retains them as missing. Window means are retrospective descriptive per-run summaries, not confirmatory convergence tests. Historical Run9 seed unavailable; no exact historical trajectory, equilibrium, or paper-level verdict.",
}
(args.output / "audit.json").write_text(
    json.dumps(result, indent=2, allow_nan=False) + "\n"
)
print(
    json.dumps({"runs": len(seen), "counts": counts, "max_definition_error": max_error})
)
