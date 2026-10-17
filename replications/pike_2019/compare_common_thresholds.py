"""Compare complete audited common-resource grids; preserve numerical failures."""

import argparse
import csv
import hashlib
import itertools
import json
import math
from pathlib import Path
import statistics

import numpy as np
from scipy.stats import t

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("ten", type=Path)
parser.add_argument("output", type=Path)
parser.add_argument(
    "--five",
    nargs=2,
    type=Path,
    action="append",
    required=True,
    metavar=("RUN", "AUDIT"),
)
args = parser.parse_args()
assert not args.output.exists()
variants = ["common-one", "common-multi"]
expected = [(seed, variant) for seed in range(100) for variant in variants]
reports = []
inputs = {}
measurements = {5: [], 10: []}
for run, audit in args.five:
    raw = (audit / "audit.json").read_bytes()
    report = json.loads(raw)
    assert report["threshold"] == 5 and report["required_runs"] == 200
    assert (
        report["analyzer_sha256"]
        == hashlib.sha256(
            Path(__file__).with_name("audit_common_resources.py").read_bytes()
        ).hexdigest()
    )
    start, stop = report["ordinal_interval"]
    assert len(report["runs"]) == report["structurally_audited_runs"] == stop - start
    assert [(r["numpy_seed"], r["variant"]) for r in report["runs"]] == expected[
        start:stop
    ]
    for name, key in [
        ("manifest.json", "manifest_sha256"),
        ("completed.jsonl", "ledger_sha256"),
    ]:
        content = (run / name).read_bytes()
        assert hashlib.sha256(content).hexdigest() == report[key]
        inputs[str(run / name)] = report[key]
    ledger = [
        json.loads(line) for line in (run / "completed.jsonl").read_text().splitlines()
    ]
    assert len(ledger) == stop - start
    for record in ledger:
        native = run / f"{record['variant']}-{record['seed']}"
        for name, checksum in record["sha256"].items():
            assert hashlib.sha256((native / name).read_bytes()).hexdigest() == checksum
    inputs[str(audit / "audit.json")] = hashlib.sha256(raw).hexdigest()
    data = (audit / "price-measurements.csv").read_bytes()
    inputs[str(audit / "price-measurements.csv")] = hashlib.sha256(data).hexdigest()
    measurements[5].extend(csv.DictReader(data.decode().splitlines()))
    reports.append(report)
reports.sort(key=lambda r: r["ordinal_interval"][0])
assert reports[0]["ordinal_interval"][0] == 0
assert reports[-1]["ordinal_interval"][1] == 200
assert all(
    a["ordinal_interval"][1] == b["ordinal_interval"][0]
    for a, b in zip(reports, reports[1:])
)
runs = {5: [run for report in reports for run in report["runs"]]}
ten_raw = (args.ten / "reconciliation.json").read_bytes()
ten = json.loads(ten_raw)
assert ten["threshold"] == 10 and ten["complete_grid"]
assert ten["structurally_audited_runs"] == ten["required_runs"] == 200
for name, checksum in ten["input_sha256"].items():
    assert hashlib.sha256(Path(name).read_bytes()).hexdigest() == checksum
inputs[str(args.ten / "reconciliation.json")] = hashlib.sha256(ten_raw).hexdigest()
runs[10] = ten["runs"]
ten_prices = (args.ten / "price-measurements.csv").read_bytes()
inputs[str(args.ten / "price-measurements.csv")] = hashlib.sha256(
    ten_prices
).hexdigest()
measurements[10] = list(csv.DictReader(ten_prices.decode().splitlines()))
dispersions = {}
for threshold in [5, 10]:
    assert len(runs[threshold]) == 200
    assert {(r["numpy_seed"], r["variant"]) for r in runs[threshold]} == set(expected)
    runs[threshold].sort(key=lambda r: (r["numpy_seed"], variants.index(r["variant"])))
    rows = measurements[threshold]
    assert len(rows) == 200000
    assert {(r["variant"], int(r["numpy_seed"]), int(r["step"])) for r in rows} == set(
        itertools.product(variants, range(100), range(1, 1001))
    )
    for variant in variants:
        selected = [r for r in rows if r["variant"] == variant]
        assert len(selected) == 100000
        assert all(
            bool(r["sample_sd_log_price"]) == (int(r["trades"]) >= 2) for r in selected
        )
        values = np.array(
            [
                float(r["sample_sd_log_price"])
                for r in selected
                if r["sample_sd_log_price"]
            ]
        )
        assert len(values) > 0 and np.isfinite(values).all() and (values >= 0).all()
        dispersions[threshold, variant] = values
comparisons = []
paired_rows = []
for variant in variants:
    five = [r for r in runs[5] if r["variant"] == variant]
    ten_runs = [r for r in runs[10] if r["variant"] == variant]
    differences = [
        a["final_individual_agents"] - b["final_individual_agents"]
        for a, b in zip(five, ten_runs)
    ]
    assert len(differences) == 100
    mean = statistics.fmean(differences)
    radius = float(t.ppf(0.975, 99)) * statistics.stdev(differences) / math.sqrt(100)
    comparisons.append(
        {
            "variant": variant,
            "threshold5_mean": statistics.fmean(
                r["final_individual_agents"] for r in five
            ),
            "threshold10_mean": statistics.fmean(
                r["final_individual_agents"] for r in ten_runs
            ),
            "paired_difference": {
                "n": 100,
                "mean": mean,
                "low": mean - radius,
                "high": mean + radius,
            },
        }
    )
    paired_rows.extend(
        {
            "variant": variant,
            "seed": i,
            "threshold5": a["final_individual_agents"],
            "threshold10": b["final_individual_agents"],
            "difference": differences[i],
        }
        for i, (a, b) in enumerate(zip(five, ten_runs))
    )
common_edges = np.histogram_bin_edges(
    np.concatenate(list(dispersions.values())), bins=500
)
histograms = []
for (threshold, variant), values in dispersions.items():
    for kind, bins in [
        ("notebook_separate_ranges", 500),
        ("common_edges", common_edges),
    ]:
        counts, edges = np.histogram(values, bins=bins)
        assert int(counts.sum()) == len(values)
        peak = int(np.argmax(counts))
        histograms.append(
            {
                "threshold": threshold,
                "variant": variant,
                "construction": kind,
                "defined_steps": len(values),
                "undefined_steps": 100000 - len(values),
                "counts": counts.tolist(),
                "edges": edges.tolist(),
                "maximum_bin": {
                    "index": peak,
                    "count": int(counts[peak]),
                    "left": float(edges[peak]),
                    "right": float(edges[peak + 1]),
                },
            }
        )
args.output.mkdir(parents=True)
with (args.output / "paired-survivors.csv").open("x") as stream:
    writer = csv.DictWriter(stream, fieldnames=list(paired_rows[0]))
    writer.writeheader()
    writer.writerows(paired_rows)
result = {
    "conditions": 400,
    "threshold5_runs": 200,
    "threshold10_runs": 200,
    "numerically_failed_runs": {
        str(k): sum(r["numeric_validation"] == "failed" for r in v)
        for k, v in runs.items()
    },
    "survivor_comparisons": comparisons,
    "histograms": histograms,
    "input_sha256": inputs,
    "scope": "Complete native grids. Seed-paired pointwise 95% Student-t intervals. Notebook histograms pool defined per-step log-price sample deviations into 500 bins; shared edges are a separate diagnostic. Maximum-bin changes do not identify the paper's unspecified central bin or prove shape equivalence. Native nonfinite holdings preclude positive economic-validation credit. No paper verdict.",
}
(args.output / "comparison.json").write_text(
    json.dumps(result, indent=2, allow_nan=False) + "\n"
)
print(
    json.dumps(
        {k: v for k, v in result.items() if k not in ["histograms", "input_sha256"]}
    )
)
