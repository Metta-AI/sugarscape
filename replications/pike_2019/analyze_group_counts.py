"""Recover ungrouped-agent counts from complete audited nonnested ensembles."""

import argparse
import csv
import hashlib
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
parser.add_argument("controls", type=Path)
parser.add_argument("output", type=Path)
args = parser.parse_args()
control_path = args.controls / "complete.json"
control = json.loads(control_path.read_text())
assert (
    control["validated_runs"] == 4
    and control["validated_steps"] == 4000
    and control["exact_raw_files"] == 20
)
assert {(r["approach"], r["policy"]) for r in control["runs"]} == {
    (a, p) for a in ["explicit", "network"] for p in ["none", "movement"]
}
values = {}
input_hashes = {
    str(control_path): hashlib.sha256(control_path.read_bytes()).hexdigest()
}
observations = 0
for directory, phase, required in [(args.phase3, 3, 1200), (args.phase2, 2, 600)]:
    report_path = directory / "reconciliation.json"
    report = json.loads(report_path.read_text())
    assert (
        report["phase"] == phase
        and report["complete_grid"]
        and report["validated_runs"] == required
    )
    input_hashes[str(report_path)] = hashlib.sha256(
        report_path.read_bytes()
    ).hexdigest()
    for segment in report["segments"]:
        source = Path(segment["run"])
        ledger = (source / "completed.jsonl").read_bytes()
        assert hashlib.sha256(ledger).hexdigest() == segment["ledger_sha256"]
        for record in map(json.loads, ledger.splitlines()):
            selector = record["selector"] if phase == 3 else "none"
            condition = f"{record['approach']}-{record['threshold']}-{selector}"
            key = (condition, record["seed"])
            assert key not in values
            prefix = "configured/run" if selector == "corrected-highest" else "run"
            relative = prefix + "/observations.json"
            target = source / Path(record["command"][-1]).name / relative
            raw = target.read_bytes()
            assert hashlib.sha256(raw).hexdigest() == record["sha256"][relative]
            rows = json.loads(raw)
            assert [r["step"] for r in rows] == list(range(1, 1001))
            assert all(r["nested_group_edges"] == 0 for r in rows)
            independent = [
                r["native_reporter"] - 2500 - r["retained_groups"] for r in rows
            ]
            assert all(
                isinstance(n, int) and 0 <= n <= r["individual_agents"]
                for n, r in zip(independent, rows, strict=True)
            )
            values[key] = {
                "final_independent": independent[-1],
                "late_mean_independent": statistics.fmean(independent[-100:]),
            }
            observations += len(rows)
assert len(values) == 1800 and observations == 1800000
estimates = []
comparisons = []
for condition in sorted({key[0] for key in values}):
    for metric in ["final_independent", "late_mean_independent"]:
        estimates.append(
            {
                "condition": condition,
                "metric": metric,
                **interval([values[condition, seed][metric] for seed in range(100)]),
            }
        )
for approach in ["explicit", "network"]:
    for threshold in [1, 5, 10]:
        for selector in ["released", "corrected-highest"]:
            left, right = (
                f"{approach}-{threshold}-{selector}",
                f"{approach}-{threshold}-none",
            )
            for metric in ["final_independent", "late_mean_independent"]:
                comparisons.append(
                    {
                        "left": left,
                        "right": right,
                        "metric": metric,
                        **interval(
                            [
                                values[left, seed][metric] - values[right, seed][metric]
                                for seed in range(100)
                            ]
                        ),
                    }
                )
args.output.mkdir(parents=True, exist_ok=False)
(args.output / "analysis.json").write_text(
    json.dumps(
        {
            "observations": observations,
            "input_sha256": input_hashes,
            "estimates": estimates,
            "paired_movement_differences": comparisons,
            "scope": "Ungrouped agents recovered as active schedule minus2500 permanent resources and retained groups. All observations require no nested groups; four native1000-step controls establish reporter identity and trajectory parity. Pointwise95% intervals; no historical source claim.",
        },
        indent=2,
    )
    + "\n"
)
with (args.output / "run-measurements.csv").open("x") as stream:
    writer = csv.DictWriter(
        stream,
        fieldnames=["condition", "seed", "final_independent", "late_mean_independent"],
    )
    writer.writeheader()
    writer.writerows(
        {"condition": condition, "seed": seed, **metrics}
        for (condition, seed), metrics in sorted(values.items())
    )
print(json.dumps({"runs": len(values), "observations": observations}))
