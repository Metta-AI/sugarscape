"""Audit the complete subsistence ensemble and compare exported Figure 6(a) vertices."""

import argparse
import csv
import hashlib
import json
import math
from pathlib import Path

import numpy as np

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("experiment", type=Path)
parser.add_argument("extraction", type=Path)
parser.add_argument("output", type=Path)
args = parser.parse_args()
root = args.experiment.resolve()
manifest = json.loads((root / "manifest.json").read_text())
for name, digest in manifest["sha256"].items():
    assert hashlib.sha256((root / name).read_bytes()).hexdigest() == digest
assert json.loads((root / "complete.json").read_text())["complete_runs"] == 200
protocol = json.loads((root / "protocol.json").read_text())
assert (
    protocol["metabolism"] == 4
    and protocol["cycles"] == 505
    and protocol["seeds"] == list(range(100))
)
assert json.loads((root / "qualification.json").read_text()) == {
    "complete_native_pairs": 2,
    "cycles_per_pair": 1000,
    "aggregate_and_individual_outputs_byte_exact": True,
}
records = [json.loads(s) for s in (root / "completed.jsonl").read_text().splitlines()]
assert [(r["infertility"], r["seed"]) for r in records] == [
    (f, s) for f in [5, 10] for s in range(100)
]
values = {f: np.zeros((100, 505), dtype=np.int64) for f in [5, 10]}
for record in records:
    f, seed = record["infertility"], record["seed"]
    directory = root / "runs" / f"{f}-{seed}"
    for name, digest in record["sha256"].items():
        assert hashlib.sha256((directory / name).read_bytes()).hexdigest() == digest
    terminal = json.loads((directory / "exit.json").read_text())
    assert terminal["exit_code"] == 0
    assert terminal["command"] == [
        str(root / "generalized"),
        str(seed),
        str(f),
        "0",
        "505",
        "1",
        str(directory / "observations.csv"),
        "4",
    ]
    with (directory / "aggregate.csv").open() as stream:
        rows = list(csv.DictReader(stream))
    assert len(rows) == record["cycles"] == 505, (
        "No partial/extinct trajectory is silently dropped from the pointwise ensemble"
    )
    old_population, old_total = 1, 10000
    for cycle, row in enumerate(rows, 1):
        assert int(row["cycle"]) == cycle and all(
            math.isfinite(float(v)) for v in row.values()
        )
        integer = {k: int(v) for k, v in row.items() if k not in ["mean_age", "gini"]}
        assert all(v >= 0 for v in integer.values())
        n = integer["population"]
        births = integer["births"]
        deaths = integer["deaths"]
        assert 0 < n <= 2500 and n == old_population + births - deaths
        assert integer["metabolism"] == 4 * (old_population - deaths)
        assert (
            integer["wealth"]
            == integer["birth_loss"]
            == integer["conservation_error"]
            == 0
        )
        assert float(row["gini"]) == 0 and float(row["mean_age"]) >= 0
        assert integer["death_loss"] <= 3 * deaths
        assert 0 <= integer["landscape"] <= 10000 and 0 <= integer["growth"] <= 2500
        total = integer["landscape"] + integer["wealth"]
        assert (
            total
            == old_total
            + integer["growth"]
            - integer["metabolism"]
            - integer["death_loss"]
            - integer["birth_loss"]
        )
        old_total, old_population = total, n
        values[f][seed, cycle - 1] = n
    assert int(rows[-1]["population"]) == record["final_population"]
extracted = json.loads((args.extraction / "audit.json").read_text())
rows = []
summaries = []
for curve in extracted["curves"]:
    path = args.extraction / curve["file"]
    assert hashlib.sha256(path.read_bytes()).hexdigest() == curve["sha256"]
    if curve["kind"] != "actual":
        continue
    f = curve["infertility"]
    samples = values[f]
    curve_rows = []
    with path.open() as stream:
        for point in csv.DictReader(stream):
            time = float(point["approximate_cycle"])
            cycle = round(time)
            assert abs(time - cycle) < 0.02
            if cycle == 0:
                continue
            assert 1 <= cycle <= 505
            published = float(point["approximate_population"])
            mean = float(samples[:, cycle - 1].mean())
            low, high = np.percentile(samples[:, cycle - 1], [2.5, 97.5])
            row = {
                "infertility": f,
                "cycle": cycle,
                "region": "visible" if cycle <= 200 else "exported_beyond_axis",
                "approximate_published_population": published,
                "seed_mean": mean,
                "seed_p025": float(low),
                "seed_p975": float(high),
                "inside_pointwise_band": bool(low <= published <= high),
                "mean_difference": mean - published,
            }
            rows.append(row)
            curve_rows.append(row)
    for region in ["visible", "exported_beyond_axis"]:
        selected = [r for r in curve_rows if r["region"] == region]
        summaries.append(
            {
                "infertility": f,
                "region": region,
                "observed_vertices": len(selected),
                "inside_pointwise_band": sum(
                    r["inside_pointwise_band"] for r in selected
                ),
                "rms_mean_difference": math.sqrt(
                    math.fsum(r["mean_difference"] ** 2 for r in selected)
                    / len(selected)
                ),
            }
        )
args.output.mkdir(parents=True, exist_ok=False)
with (args.output / "comparison.csv").open("w") as stream:
    writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
    writer.writeheader()
    writer.writerows(rows)
np.savez_compressed(
    args.output / "populations.npz", infertility5=values[5], infertility10=values[10]
)
report = {
    "complete_native_runs": 200,
    "audited_cycles": 101000,
    "zero_wealth_and_gini_all_observations": True,
    "independent_population_and_resource_balance_checks": 101000,
    "comparison_rows": len(rows),
    "summaries": summaries,
    "protocol_sha256": hashlib.sha256(
        (root / "protocol.json").read_bytes()
    ).hexdigest(),
    "extraction_audit_sha256": hashlib.sha256(
        (args.extraction / "audit.json").read_bytes()
    ).hexdigest(),
    "populations_sha256": hashlib.sha256(
        (args.output / "populations.npz").read_bytes()
    ).hexdigest(),
    "scope": "Conditional Figure6(a) reconstruction. Pointwise seed bands are descriptive, not a simultaneous equivalence test. Original seed, phase and simulation implementation remain unresolved; no omitted vector observations are fabricated.",
}
(args.output / "audit.json").write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps(report))
