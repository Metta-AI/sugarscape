"""Analyze audited movement and no-policy ensembles with seeds as sampling units."""

import argparse
import csv
import hashlib
import itertools
import json
import math
from pathlib import Path
import statistics

from scipy.stats import t


def interval(values):
    mean = statistics.fmean(values)
    radius = (
        float(t.ppf(0.975, len(values) - 1))
        * statistics.stdev(values)
        / math.sqrt(len(values))
    )
    return {"n": len(values), "mean": mean, "low": mean - radius, "high": mean + radius}


parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("phase3", type=Path)
parser.add_argument("phase2", type=Path)
parser.add_argument("output", type=Path)
args = parser.parse_args()
conditions = {}
hashes = {}
rows = []
for directory, phase, required in [(args.phase3, 3, 1200), (args.phase2, 2, 600)]:
    path = directory / "reconciliation.json"
    raw = path.read_bytes()
    report = json.loads(raw)
    assert report["phase"] == phase and report["complete_grid"]
    assert report["validated_runs"] == report["required_runs"] == required
    assert report["missing_ordinals"] == []
    assert [r["ordinal"] for r in report["runs"]] == list(range(required))
    hashes[str(path)] = hashlib.sha256(raw).hexdigest()
    for index, segment in enumerate(report["segments"]):
        audit = directory / f"segment-{index:02d}" / "audit.json"
        assert hashlib.sha256(audit.read_bytes()).hexdigest() == segment["audit_sha256"]
    for run in report["runs"]:
        selector = run["selector"] if phase == 3 else "none"
        key = (run["approach"], run["threshold"], selector)
        label = "-".join(map(str, key))
        values = {
            "survivors": run["final_individual_agents"],
            "undefined_dispersion_steps": run["undefined_dispersion_steps"],
        }
        for window in ["early", "late"]:
            values[f"{window}_trades"] = run["windows"][window]["trades"]
            for metric in ["geometric_mean_price", "sample_sd_log_price"]:
                values[f"{window}_{metric}"] = run["windows"][window][metric][
                    "mean_over_defined_steps"
                ]
                values[f"{window}_{metric}_defined_steps"] = run["windows"][window][
                    metric
                ]["defined_steps"]
        seed = run["numpy_seed"]
        conditions.setdefault(key, {})
        assert seed not in conditions[key]
        conditions[key][seed] = values
        rows.extend(
            {"condition": label, "seed": seed, "metric": metric, "value": value}
            for metric, value in values.items()
        )
expected = set(
    itertools.product(
        ["explicit", "network"], [1, 5, 10], ["none", "released", "corrected-highest"]
    )
)
assert set(conditions) == expected
assert all(set(v) == set(range(100)) for v in conditions.values())
metrics = list(conditions[("explicit", 1, "none")][0])
estimates = []
for key, runs in sorted(conditions.items()):
    for metric in metrics:
        defined = [
            runs[seed][metric] for seed in range(100) if runs[seed][metric] is not None
        ]
        estimates.append(
            {
                "condition": "-".join(map(str, key)),
                "metric": metric,
                "defined_runs": len(defined),
                "interval": interval(defined) if len(defined) >= 2 else None,
            }
        )
# Compare one factor at a time. No-policy contrasts use the same assigned seeds.
pairs = []
for approach, threshold in itertools.product(["explicit", "network"], [1, 5, 10]):
    for selector in ["released", "corrected-highest"]:
        pairs.append(
            (
                "movement_vs_none",
                (approach, threshold, selector),
                (approach, threshold, "none"),
            )
        )
    pairs.append(
        (
            "selector",
            (approach, threshold, "corrected-highest"),
            (approach, threshold, "released"),
        )
    )
for selector in ["released", "corrected-highest"]:
    for threshold in [1, 5, 10]:
        pairs.append(
            (
                "approach",
                ("network", threshold, selector),
                ("explicit", threshold, selector),
            )
        )
    for approach in ["explicit", "network"]:
        for low, high in itertools.combinations([1, 5, 10], 2):
            pairs.append(
                ("threshold", (approach, high, selector), (approach, low, selector))
            )
assert len(pairs) == 36
comparisons = []
for kind, left, right in pairs:
    for metric in metrics:
        differences = [
            conditions[left][seed][metric] - conditions[right][seed][metric]
            for seed in range(100)
            if conditions[left][seed][metric] is not None
            and conditions[right][seed][metric] is not None
        ]
        comparisons.append(
            {
                "kind": kind,
                "left": "-".join(map(str, left)),
                "right": "-".join(map(str, right)),
                "metric": metric,
                "defined_pairs": len(differences),
                "interval": interval(differences) if len(differences) >= 2 else None,
            }
        )
result = {
    "input_sha256": hashes,
    "estimates": estimates,
    "paired_differences": comparisons,
    "scope": "Complete 1200 movement and 600 no-policy trajectories. Seed-level pointwise Student-t 95% intervals, not simultaneous intervals. Each metric has 36 contrasts. Price/dispersion means and differences condition on defined observations and jointly defined seed pairs; undefined values are not zeros. Corrected selectors are sensitivity experiments, not historical replication. No equivalence margin or authenticated paper revision; no paper-level verdict. Histograms and historical figure comparisons remain separate.",
}
args.output.mkdir(parents=True, exist_ok=False)
(args.output / "analysis.json").write_text(
    json.dumps(result, indent=2, allow_nan=False) + "\n"
)
with (args.output / "run-measurements.csv").open("x") as stream:
    writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
    writer.writeheader()
    writer.writerows(rows)
print(
    json.dumps(
        {
            "conditions": len(conditions),
            "runs": 1800,
            "metrics": len(metrics),
            "contrasts_per_metric": len(pairs),
        }
    )
)
