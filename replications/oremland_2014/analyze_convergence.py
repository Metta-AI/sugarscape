"""Audit the complete native convergence ensemble and report every policy."""

import argparse
import csv
import gzip
import hashlib
import json
from pathlib import Path
from typing import Literal

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from pydantic import BaseModel, ConfigDict, Field


class Request(BaseModel):
    model_config = ConfigDict(extra="forbid")
    id: int = Field(ge=0, lt=20000)
    seed: int = Field(ge=1, le=100)
    phase: Literal[0, 4]
    clipped: Literal[False]
    policy: list[Literal[0.0, 0.25, 0.5, 0.75]] = Field(min_length=200, max_length=200)


class Result(BaseModel):
    model_config = ConfigDict(extra="forbid")
    id: int = Field(ge=0, lt=20000)
    seed: int = Field(ge=1, le=100)
    phase: Literal[0, 4]
    clipped: Literal[False]
    steps: Literal[50]
    population: int = Field(ge=0, le=200)
    total_tax: int
    debt_refund: int = Field(ge=0, le=600)
    state_sha256: str = Field(pattern="^[a-f0-9]{64}$")
    elapsed_seconds: float = Field(gt=0, allow_inf_nan=False)


parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("experiment", type=Path)
parser.add_argument("output", type=Path)
args = parser.parse_args()
root = args.experiment
run = root / "execution"
protocol = json.loads((root / "protocol.json").read_text())
manifest = json.loads((run / "manifest.json").read_text())
assert json.loads((run / "exit.json").read_text())["exit_codes"] == [0] * 4
for name, digest in protocol["files_sha256"].items():
    assert hashlib.sha256((root / name).read_bytes()).hexdigest() == digest
for name in [
    "RunPolicyBatch.java",
    "RunPolicyBatch.class",
    "oremland.nlogo",
    "sugar-map.txt",
]:
    assert (
        hashlib.sha256((run / name).read_bytes()).hexdigest()
        == manifest["sha256"][name]
    )
assert (
    hashlib.sha256((root / "protocol.json").read_bytes()).hexdigest()
    == manifest["sha256"]["protocol.json"]
)
reference_path = (
    Path(__file__).parent / "results/batch-evaluator-2026-10-18/manifest.json"
)
reference = json.loads(reference_path.read_text())
assert manifest["sha256"]["RunPolicyBatch.java"] == reference["source_sha256"]
assert manifest["sha256"]["oremland.nlogo"] == reference["model_sha256"]
assert manifest["jars"] == reference["jars"]
assert (
    manifest["sha256"]["sugar-map.txt"]
    == "cd9b4661c8813d3e268995676d5ba84394ee813986adb0d657dc9be4a1fab675"
)
policies = json.loads((root / "policies.json").read_text())
assert len(policies) == 100
values = np.full((100, 2, 100, 3), np.nan)
seen = set()
refunds = []
for worker in range(4):
    assert json.loads((run / f"exit-{worker}.json").read_text())["exit_code"] == 0
    with (
        (root / f"requests-{worker}.jsonl").open() as inputs,
        (run / f"results-{worker}.jsonl").open() as outputs,
    ):
        for input_line, output_line in zip(inputs, outputs, strict=True):
            request = Request.model_validate_json(input_line)
            result = Result.model_validate_json(output_line)
            assert request.id == result.id and request.id % 4 == worker
            assert (request.seed, request.phase, request.clipped) == (
                result.seed,
                result.phase,
                result.clipped,
            )
            assert result.id not in seen
            seen.add(result.id)
            policy_id, offset = divmod(result.id, 200)
            phase_index, seed_index = divmod(offset, 100)
            assert result.phase == [0, 4][phase_index] and result.seed == seed_index + 1
            policy = policies[policy_id]
            assert policy["id"] == policy_id
            assert request.policy == [value / 4 for value in policy["quarter_units"]]
            assert sum(request.policy) / 200 == policy["mean_rate"]
            assert result.total_tax + result.debt_refund >= 0
            values[policy_id, phase_index, seed_index] = [
                200 - result.population,
                result.total_tax,
                result.total_tax + result.debt_refund,
            ]
            refunds.append(result.debt_refund)
assert seen == set(range(20000)) and np.isfinite(values).all()
args.output.mkdir(parents=True, exist_ok=False)
metrics = ["deaths", "literal_revenue", "derived_clipped_revenue"]
summary_rows = []
with gzip.open(args.output / "prefix-curves.csv.gz", "wt", newline="") as stream:
    writer = csv.writer(stream)
    writer.writerow(
        [
            "policy_id",
            "mean_rate",
            "phase",
            "seeds",
            "metric",
            "mean",
            "population_sd",
            "sample_sd",
        ]
    )
    for policy_id in range(100):
        for phase_index, phase in enumerate([0, 4]):
            for metric_index, metric in enumerate(metrics):
                data = values[policy_id, phase_index, :, metric_index]
                for n in range(2, 101):
                    writer.writerow(
                        [
                            policy_id,
                            policies[policy_id]["mean_rate"],
                            phase,
                            n,
                            metric,
                            data[:n].mean(),
                            data[:n].std(ddof=0),
                            data[:n].std(ddof=1),
                        ]
                    )
                first, second = data[:50], data[50:]
                summary_rows.append(
                    {
                        "policy_id": policy_id,
                        "mean_rate": policies[policy_id]["mean_rate"],
                        "phase": phase,
                        "metric": metric,
                        "mean_50": float(first.mean()),
                        "mean_100": float(data.mean()),
                        "mean_change_50_to_100": float(data.mean() - first.mean()),
                        "sample_sd_50": float(first.std(ddof=1)),
                        "sample_sd_100": float(data.std(ddof=1)),
                        "sample_sd_change_50_to_100": float(
                            data.std(ddof=1) - first.std(ddof=1)
                        ),
                        "second_half_minus_first_half_mean": float(
                            second.mean() - first.mean()
                        ),
                        "half_difference_standard_error": float(
                            np.sqrt(first.var(ddof=1) / 50 + second.var(ddof=1) / 50)
                        ),
                    }
                )
with (args.output / "policy-summaries.csv").open("x", newline="") as stream:
    writer = csv.DictWriter(stream, fieldnames=list(summary_rows[0]))
    writer.writeheader()
    writer.writerows(summary_rows)
aggregates = []
for phase in [0, 4]:
    for metric in metrics:
        rows = [
            row
            for row in summary_rows
            if row["phase"] == phase and row["metric"] == metric
        ]
        aggregates.append(
            {
                "phase": phase,
                "metric": metric,
                **{
                    key: {
                        "minimum": float(np.min([row[key] for row in rows])),
                        "median": float(np.median([row[key] for row in rows])),
                        "maximum": float(np.max([row[key] for row in rows])),
                    }
                    for key in [
                        "mean_100",
                        "mean_change_50_to_100",
                        "sample_sd_change_50_to_100",
                        "half_difference_standard_error",
                    ]
                },
            }
        )
colors = {0.125: "#1f77b4", 0.25: "#ff7f0e", 0.375: "#2ca02c"}
for phase_index, phase in enumerate([0, 4]):
    fig, axes = plt.subplots(2, 3, figsize=(13, 7))
    for policy_id in range(100):
        for metric_index, metric in enumerate(metrics):
            data = values[policy_id, phase_index, :, metric_index]
            for row, statistic in enumerate([np.mean, lambda x: np.std(x, ddof=1)]):
                axes[row, metric_index].plot(
                    range(2, 101),
                    [statistic(data[:n]) for n in range(2, 101)],
                    color=colors[policies[policy_id]["mean_rate"]],
                    alpha=0.25,
                    linewidth=0.6,
                )
    for column, metric in enumerate(metrics):
        axes[0, column].set_title(metric.replace("_", " "))
        for row in range(2):
            axes[row, column].set_xlabel("Simulation seeds in prefix")
            axes[row, column].axvline(50, color="black", linewidth=0.6, linestyle="--")
    axes[0, 0].set_ylabel("Mean")
    axes[1, 0].set_ylabel("Sample standard deviation")
    fig.suptitle(
        f"Reconstructed policies; first tax after move {phase + 1}\n100 curves per panel; mean tax rate: blue 0.125, orange 0.25, green 0.375"
    )
    fig.tight_layout()
    fig.savefig(args.output / f"convergence-phase-{phase}.png", dpi=150)
    plt.close(fig)
report = {
    "complete_native_runs": len(seen),
    "qualified_reference_manifest_sha256": hashlib.sha256(
        reference_path.read_bytes()
    ).hexdigest(),
    "validated_request_result_lines": 2 * len(seen),
    "policies": 100,
    "seeds_per_policy_phase": 100,
    "prefix_summary_rows": 59400,
    "refund_minimum": min(refunds),
    "refund_maximum": max(refunds),
    "aggregates": aggregates,
    "scope": "Conditional reconstruction, not exact original Figure 9. No pass threshold or whole-paper completion assigned. Clipped revenue is derived, not an additional simulation. Half-difference standard errors describe within-policy seed variation; policies share seeds and are not independent replicates.",
    "inputs_sha256": {
        str(path.relative_to(root)): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in [
            root / "protocol.json",
            root / "policies.json",
            run / "manifest.json",
            run / "exit.json",
            *sorted(run.glob("results-*.jsonl")),
        ]
    },
}
(args.output / "audit.json").write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps(report))
