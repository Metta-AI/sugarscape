"""Compare the complete conditional ensemble with labelled original Figure 4 curves."""

import argparse
import csv
import gzip
import hashlib
import json
from pathlib import Path

import numpy as np

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("experiment", type=Path)
parser.add_argument("figure", type=Path)
parser.add_argument("output", type=Path)
parser.add_argument("--scenario", choices=["stable", "chaotic"], default="stable")
args = parser.parse_args()
minimum_fertility = 10 if args.scenario == "stable" else 1
protocol = json.loads((args.experiment / "protocol.json").read_text())
assert protocol["seeds"] == list(range(100)) and protocol["cycles"] == 500
manifest = json.loads((args.experiment / "manifest.json").read_text())
for name, digest in manifest["sha256"].items():
    assert hashlib.sha256((args.experiment / name).read_bytes()).hexdigest() == digest
ledger = [
    json.loads(line)
    for line in (args.experiment / "completed.jsonl").read_text().splitlines()
]
assert [r["seed"] for r in ledger] == list(range(100))
assert (
    json.loads((args.experiment / "complete.json").read_text())["complete_runs"] == 100
)
# Axes: seed, cycle 1..500, population/wealth/gini/f10/bc0/joint-optimum/mean-age.
values = np.zeros((100, 500, 7), dtype=float)
for record in ledger:
    seed = record["seed"]
    root = args.experiment / "runs" / str(seed)
    assert record["cycles"] == 500
    command = json.loads((root / "exit.json").read_text())["command"]
    assert command[2:6] == [str(minimum_fertility), "10", "500", "1"]
    for name, digest in record["sha256"].items():
        assert hashlib.sha256((root / name).read_bytes()).hexdigest() == digest
    with (root / "aggregate.csv").open() as stream:
        for r in csv.DictReader(stream):
            t = int(r["cycle"]) - 1
            values[seed, t, 6] = float(r["mean_age"])
            values[seed, t, :3] = [
                int(r["population"]),
                int(r["wealth"]),
                float(r["gini"]),
            ]
    with (root / "traits.csv").open() as stream:
        for r in csv.DictReader(stream):
            if r["kind"] != "joint" or int(r["cycle"]) == 0:
                continue
            t = int(r["cycle"]) - 1
            f = int(r["infertility"])
            cost = int(r["birth_cost"])
            n = int(r["count"])
            if f == minimum_fertility:
                values[seed, t, 3] += n
            if cost == 0:
                values[seed, t, 4] += n
            if f == minimum_fertility and cost == 0:
                values[seed, t, 5] += n
assert np.isfinite(values).all()
args.output.mkdir(parents=True, exist_ok=False)
np.savez_compressed(args.output / "ensemble.npz", values=values)
with np.load(args.output / "ensemble.npz") as restored:
    assert np.array_equal(restored["values"], values)
figure = json.loads((args.figure / "audit.json").read_text())
rows = []
comparison_series = (
    [
        ("infertility_10", 3),
        ("birth_cost_0", 4),
        ("wealth", 1),
        ("gini", 2),
    ]
    if args.scenario == "stable"
    else []
)
for name, column in comparison_series:
    entry = next(r for r in figure["series"] if r["series"] == name)
    path = args.figure / (name + ".csv.gz")
    assert hashlib.sha256(path.read_bytes()).hexdigest() == entry["sha256"]
    with gzip.open(path, "rt") as stream:
        for r in csv.DictReader(stream):
            time = float(r["approximate_generation"])
            t = round(time)
            assert abs(time - t) < 0.05
            if t == 0:
                continue
            samples = values[:, t - 1, column]
            low, high = np.percentile(samples, [2.5, 97.5])
            rows.append(
                {
                    "series": name,
                    "approximate_published_generation": time,
                    "assumed_action_cycle": t,
                    "published_value": float(r["approximate_value"]),
                    "ensemble_mean": float(samples.mean()),
                    "ensemble_p2_5": float(low),
                    "ensemble_p97_5": float(high),
                }
            )
with (args.output / "comparison.csv").open("x", newline="") as stream:
    writer = csv.DictWriter(
        stream,
        fieldnames=[
            "series",
            "approximate_published_generation",
            "assumed_action_cycle",
            "published_value",
            "ensemble_mean",
            "ensemble_p2_5",
            "ensemble_p97_5",
        ],
        lineterminator="\n",
    )
    writer.writeheader()
    writer.writerows(rows)
summary = {}
for name, column in [
    ("population", 0),
    ("wealth", 1),
    ("gini", 2),
    ("minimum_infertility", 3),
    ("birth_cost_0", 4),
    ("joint_optimum", 5),
    ("mean_age", 6),
]:
    samples = values[:, 498, column]
    summary[name] = {
        "cycle": 499,
        "mean": float(samples.mean()),
        "minimum": float(samples.min()),
        "maximum": float(samples.max()),
        "p2_5": float(np.percentile(samples, 2.5)),
        "p97_5": float(np.percentile(samples, 97.5)),
    }
report = {
    "scenario": args.scenario,
    "minimum_infertility": minimum_fertility,
    "complete_runs": 100,
    "native_cycles": 50000,
    "audited_inheritance_events": sum(r["inheritance_events"] for r in ledger),
    "comparison_vertices": len(rows),
    "cycle499_summary": summary,
    "all_optimal_at_cycle499": int(np.sum(values[:, 498, 0] == values[:, 498, 5])),
    "scope": "Conditional reconstruction with declared inheritance and initialization assumptions. Pointwise central ensemble ranges are descriptive, not simultaneous confidence intervals or paper acceptance criteria. Generation equals action cycle only by assumption. No steady-state or whole-paper replication claim.",
    "sha256": {
        name: hashlib.sha256((args.output / name).read_bytes()).hexdigest()
        for name in ["ensemble.npz", "comparison.csv"]
    },
}
(args.output / "analysis.json").write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps(report))
