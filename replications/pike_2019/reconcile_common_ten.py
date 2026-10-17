"""Join the complete native cloud common-resource batch with its two seed-zero controls."""

import argparse
import csv
import hashlib
import itertools
import json
import math
from pathlib import Path
import statistics

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("batch", type=Path)
parser.add_argument("audit", type=Path)
parser.add_argument("zero", type=Path)
parser.add_argument("output", type=Path)
args = parser.parse_args()
report_path = args.audit / "audit.json"
report = json.loads(report_path.read_text())
assert (
    report["analyzer_sha256"]
    == hashlib.sha256(
        Path(__file__).with_name("audit_common_resources.py").read_bytes()
    ).hexdigest()
)
assert report["mode"] == "complete" and report["threshold"] == 10
assert report["structurally_audited_runs"] == report["required_runs"] == 198
assert report["complete_new_seed_batch"] and report["ordinal_interval"] == [0, 198]
assert json.loads((args.batch / "complete.json").read_text()) == {"completed_runs": 198}
inputs = {str(report_path): hashlib.sha256(report_path.read_bytes()).hexdigest()}
for name, key in [
    ("manifest.json", "manifest_sha256"),
    ("completed.jsonl", "ledger_sha256"),
]:
    raw = (args.batch / name).read_bytes()
    assert hashlib.sha256(raw).hexdigest() == report[key]
    inputs[str(args.batch / name)] = report[key]
manifest = json.loads((args.batch / "manifest.json").read_text())
zero_path = args.zero / "audit.json"
zero = json.loads(zero_path.read_text())
inputs[str(zero_path)] = hashlib.sha256(zero_path.read_bytes()).hexdigest()
assert {(r["variant"], r["seed"]) for r in zero["runs"]} == {
    (v, 0) for v in ["common-one", "common-multi"]
}
runs = report["runs"].copy()
measurements = []
for item in zero["runs"]:
    variant = item["variant"]
    native = args.zero / "extracted/pike-common-cloud-zero-001" / variant
    for name, digest in item["raw_sha256"].items():
        assert hashlib.sha256((native / name).read_bytes()).hexdigest() == digest
        inputs[str(native / name)] = digest
    metadata = json.loads((native / "manifest.json").read_text())
    assert metadata["runner_sha256"] == manifest["source_hashes"]["run.py"]
    other = json.loads((args.batch / f"{variant}-1/manifest.json").read_text())
    for key in [
        "python",
        "mesa",
        "numpy",
        "networkx",
        "revision",
        "library_revision",
        "source_hashes",
        "mesa_seed",
        "pythonhashseed",
    ]:
        assert metadata[key] == other[key]
    assert metadata["numpy_seed"] == metadata["policy_random_seed"] == 0
    prices = json.loads((native / "prices.json").read_text())
    rows = []
    for step in range(1, 1001):
        values = prices[str(step)] if str(step) in prices else []
        assert all(p > 0 and math.isfinite(p) for p in values)
        logs = [math.log(p) for p in values]
        rows.append(
            {
                "variant": variant,
                "numpy_seed": 0,
                "step": step,
                "trades": len(values),
                "geometric_mean_price": math.exp(statistics.fmean(logs))
                if logs
                else None,
                "sample_sd_log_price": statistics.stdev(logs)
                if len(logs) >= 2
                else None,
            }
        )
    measurements.extend(rows)
    windows = {}
    for window, start, stop in [("early", 1, 100), ("late", 901, 1000)]:
        selected = [r for r in rows if start <= r["step"] <= stop]
        windows[window] = {"trades": sum(r["trades"] for r in selected)}
        for metric in ["geometric_mean_price", "sample_sd_log_price"]:
            observed = [r[metric] for r in selected if r[metric] is not None]
            windows[window][metric] = {
                "defined_steps": len(observed),
                "mean_over_defined_steps": statistics.fmean(observed)
                if observed
                else None,
            }
    runs.append(
        {
            "variant": variant,
            "numpy_seed": 0,
            "final_individual_agents": item["final_individuals"],
            "extinct": item["final_individuals"] == 0,
            "nonfinite_health_records": item["nonfinite_health_records"],
            "first_nonfinite_step": item["first_nonfinite_step"],
            "negative_health_records": item["negative_health_records"],
            "numeric_validation": item["numeric_validation"],
            "price_steps": len(prices),
            "undefined_dispersion_steps": sum(r["trades"] < 2 for r in rows),
            "windows": windows,
        }
    )
path = args.audit / "price-measurements.csv"
inputs[str(path)] = hashlib.sha256(path.read_bytes()).hexdigest()
with path.open() as stream:
    for row in csv.DictReader(stream):
        measurements.append(
            {
                "variant": row["variant"],
                "numpy_seed": int(row["numpy_seed"]),
                "step": int(row["step"]),
                "trades": int(row["trades"]),
                **{
                    metric: float(row[metric]) if row[metric] else None
                    for metric in ["geometric_mean_price", "sample_sd_log_price"]
                },
            }
        )
assert len(runs) == 200
assert {(r["variant"], r["numpy_seed"]) for r in runs} == set(
    itertools.product(["common-one", "common-multi"], range(100))
)
assert len(measurements) == 200000
assert {(r["variant"], r["numpy_seed"], r["step"]) for r in measurements} == set(
    itertools.product(["common-one", "common-multi"], range(100), range(1, 1001))
)
for row in measurements:
    assert (row["geometric_mean_price"] is not None) == (row["trades"] > 0)
    assert (row["sample_sd_log_price"] is not None) == (row["trades"] >= 2)
args.output.mkdir(parents=True, exist_ok=False)
with (args.output / "price-measurements.csv").open("x") as stream:
    writer = csv.DictWriter(
        stream, fieldnames=list(measurements[0]), lineterminator="\n"
    )
    writer.writeheader()
    writer.writerows(
        sorted(measurements, key=lambda r: (r["numpy_seed"], r["variant"], r["step"]))
    )
result = {
    "threshold": 10,
    "complete_grid": True,
    "required_runs": 200,
    "structurally_audited_runs": len(runs),
    "health_records": report["health_records"]
    + sum(r["health_records"] for r in zero["runs"]),
    "price_step_records": len(measurements),
    "numerically_failed_runs": sum(r["numeric_validation"] == "failed" for r in runs),
    "input_sha256": inputs,
    "runs": sorted(runs, key=lambda r: (r["numpy_seed"], r["variant"])),
    "scope": "Complete homogeneous cloud threshold10 grid; seedzero included once, portability diagnostics excluded. Structural audit is not numerical/economic validity. Native nonfinite holdings remain failed observations; no positive or negative paper verdict.",
}
(args.output / "reconciliation.json").write_text(
    json.dumps(result, indent=2, allow_nan=False) + "\n"
)
print(
    json.dumps(
        {
            key: result[key]
            for key in [
                "structurally_audited_runs",
                "health_records",
                "price_step_records",
                "numerically_failed_runs",
            ]
        }
    )
)
