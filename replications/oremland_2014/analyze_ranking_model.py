"""Analyze every declared ranking convention for one fully audited model."""

import argparse
from collections import Counter
import csv
from fractions import Fraction
import hashlib
import json
import math
from pathlib import Path

import numpy as np
import scipy
from scipy.stats import rankdata

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("reference", type=Path)
parser.add_argument("model_audit", type=Path)
parser.add_argument("output", type=Path)
parser.add_argument(
    "--reference-kind", choices=["convergence", "independent"], default="convergence"
)
args = parser.parse_args()
model_report = json.loads((args.model_audit / "audit.json").read_text())
assert (
    hashlib.sha256((args.model_audit / "objectives.npz").read_bytes()).hexdigest()
    == model_report["objectives_npz_sha256"]
)
with np.load(args.model_audit / "objectives.npz") as archive:
    values = archive["objectives"]
assert list(values.shape) == model_report["objective_array_shape"]
assert values.dtype == np.int64 and values.shape[:2] == (100, 2)
assert (
    values.shape[3] == 3 and values.shape[2] == model_report["seeds_per_policy_phase"]
)
assert model_report["complete_native_runs"] == values.shape[2] * 200
if args.reference_kind == "independent":
    published = args.reference / "audit.json"
    reference_report = json.loads(published.read_text())
    assert reference_report["model"] == "50-independent-reference"
    assert (
        reference_report["seed_design"] == model_report["seed_design"] == "independent"
    )
    assert reference_report["protocol_sha256"] == model_report["protocol_sha256"]
    assert reference_report["request_id_range"][1] < model_report["request_id_range"][0]
    assert reference_report["seeds_per_policy_phase"] == 50
    assert reference_report["complete_native_runs"] == 10000
    assert reference_report["policies_sha256"] == model_report["policies_sha256"]
    assert (
        hashlib.sha256((args.reference / "objectives.npz").read_bytes()).hexdigest()
        == reference_report["objectives_npz_sha256"]
    )
    assert (
        hashlib.sha256((args.reference / "policies.json").read_bytes()).hexdigest()
        == reference_report["policies_sha256"]
    )
    policies = json.loads((args.reference / "policies.json").read_text())
    with np.load(args.reference / "objectives.npz") as archive:
        baseline = archive["objectives"]
    assert baseline.shape == (100, 2, 50, 3) and baseline.dtype == np.int64
    reference_totals = baseline.sum(axis=2)
else:
    published = Path(__file__).parent / "results/convergence-2026-10-18/audit.json"
    reference_report = json.loads(published.read_text())
    for name, digest in reference_report["inputs_sha256"].items():
        assert (
            hashlib.sha256((args.reference / name).read_bytes()).hexdigest() == digest
        )
    assert (
        hashlib.sha256((args.reference / "policies.json").read_bytes()).hexdigest()
        == model_report["policies_sha256"]
    )
    policies = json.loads((args.reference / "policies.json").read_text())
    baseline = np.full((100, 2, 100, 3), -1, dtype=np.int64)
    seen = np.zeros((100, 2, 100), dtype=np.bool_)
    for path in sorted((args.reference / "execution").glob("results-*.jsonl")):
        for line in path.read_text().splitlines():
            row = json.loads(line)
            policy_id, offset = divmod(row["id"], 200)
            phase_index, seed_index = divmod(offset, 100)
            assert row["seed"] == seed_index + 1 and row["phase"] == [0, 4][phase_index]
            assert not seen[policy_id, phase_index, seed_index]
            baseline[policy_id, phase_index, seed_index] = [
                200 - row["population"],
                row["total_tax"],
                row["total_tax"] + row["debt_refund"],
            ]
            seen[policy_id, phase_index, seed_index] = True
    assert seen.all()
    assert model_report["seed_range"] == (
        [101, 150] if model_report["width"] == 50 else [1, values.shape[2]]
    )
    reference_totals = baseline[:, :, :50].sum(axis=2)
policy_means = np.array([row["mean_rate"] for row in policies])
metrics = ["deaths", "literal_revenue", "derived_clipped_revenue"]
scopes = [
    ("pooled", np.arange(100)),
    *[
        (str(rate), np.flatnonzero(policy_means == rate))
        for rate in [0.125, 0.25, 0.375]
    ],
]
rows = []
objective_rows = []
rank_comparisons = 0
exact_kappa_checks = 0
for fraction in [Fraction(2, 100), Fraction(1, 10), Fraction(1)]:
    scaled = fraction * values.shape[2]
    low, high = max(1, math.floor(scaled)), max(1, math.ceil(scaled))
    budgets = [("floor=ceil", low)] if low == high else [("floor", low), ("ceil", high)]
    for budget_rounding, count in budgets:
        totals = values[:, :, :count].sum(axis=2)
        for phase_index, phase in enumerate([0, 4]):
            for metric_index, metric in enumerate(metrics):
                sign = 1 if metric == "deaths" else -1
                for policy_id in range(100):
                    objective_rows.append(
                        {
                            "policy_id": policy_id,
                            "mean_tax_rate": policy_means[policy_id],
                            "phase": phase,
                            "metric": metric,
                            "runtime_fraction": str(fraction),
                            "budget_rounding": budget_rounding,
                            "model_seeds": count,
                            "reference_seeds": 50,
                            "model_objective_sum": int(
                                totals[policy_id, phase_index, metric_index]
                            ),
                            "reference_objective_sum": int(
                                reference_totals[policy_id, phase_index, metric_index]
                            ),
                        }
                    )
                for scope, selection in scopes:
                    reference_scores = (
                        sign * reference_totals[selection, phase_index, metric_index]
                    )
                    model_scores = sign * totals[selection, phase_index, metric_index]
                    for ties in ["average", "ordinal"]:
                        a = rankdata(reference_scores, method=ties)
                        b = rankdata(model_scores, method=ties)
                        # Independent ordinal/tie rank reconstruction from sorted integer totals.
                        for scores, ranks in [(reference_scores, a), (model_scores, b)]:
                            order = sorted(
                                range(len(scores)),
                                key=lambda index: (int(scores[index]), index),
                            )
                            positions = {}
                            for position, index in enumerate(order, 1):
                                positions.setdefault(int(scores[index]), []).append(
                                    position
                                )
                            for index, score in enumerate(scores):
                                expected_rank = (
                                    Fraction(
                                        sum(positions[int(score)]),
                                        len(positions[int(score)]),
                                    )
                                    if ties == "average"
                                    else order.index(index) + 1
                                )
                                assert ranks[index] == float(expected_rank)
                                rank_comparisons += 1
                        doubled_a = [int(2 * value) for value in a]
                        doubled_b = [int(2 * value) for value in b]
                        count_a, count_b = Counter(doubled_a), Counter(doubled_b)
                        size = len(selection)
                        for power, weighting in [(1, "linear"), (2, "quadratic")]:
                            observed_sum = sum(
                                abs(left - right) ** power
                                for left, right in zip(
                                    doubled_a, doubled_b, strict=True
                                )
                            )
                            expected_sum = sum(
                                number_a * number_b * abs(left - right) ** power
                                for left, number_a in count_a.items()
                                for right, number_b in count_b.items()
                            )
                            observed = float(np.mean(np.abs(a - b) ** power))
                            expected = float(
                                np.mean(np.abs(a[:, None] - b[None, :]) ** power)
                            )
                            assert math.isclose(
                                observed,
                                float(Fraction(observed_sum, size * 2**power)),
                                rel_tol=0,
                                abs_tol=1e-12,
                            )
                            assert math.isclose(
                                expected,
                                float(Fraction(expected_sum, size * size * 2**power)),
                                rel_tol=0,
                                abs_tol=1e-12,
                            )
                            if expected_sum == 0:
                                kappa, status = (
                                    "",
                                    "undefined_zero_expected_disagreement",
                                )
                            else:
                                exact = Fraction(
                                    expected_sum - size * observed_sum, expected_sum
                                )
                                kappa, status = 1 - observed / expected, "defined"
                                assert math.isclose(
                                    kappa, float(exact), rel_tol=0, abs_tol=1e-12
                                )
                                exact_kappa_checks += 1
                            rows.append(
                                {
                                    "model": model_report["model"],
                                    "width": model_report["width"],
                                    "phase": phase,
                                    "metric": metric,
                                    "runtime_fraction": str(fraction),
                                    "budget_rounding": budget_rounding,
                                    "model_seeds": count,
                                    "reference_seeds": 50,
                                    "scope": scope,
                                    "policies": size,
                                    "ties": ties,
                                    "weighting": weighting,
                                    "reference_distinct_scores": len(
                                        set(reference_scores)
                                    ),
                                    "model_distinct_scores": len(set(model_scores)),
                                    "observed_disagreement": observed,
                                    "expected_disagreement": expected,
                                    "kappa": kappa,
                                    "status": status,
                                }
                            )
args.output.mkdir(parents=True, exist_ok=False)
for filename, records in [
    ("rankings.csv", rows),
    ("objective-totals.csv", objective_rows),
]:
    with (args.output / filename).open("x", newline="") as stream:
        writer = csv.DictWriter(
            stream, fieldnames=list(records[0]), lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows(records)
report = {
    "model": model_report["model"],
    "reference_kind": args.reference_kind,
    "width": model_report["width"],
    "complete_native_runs_in_model": model_report["complete_native_runs"],
    "ranking_rows": len(rows),
    "objective_rows": len(objective_rows),
    "independent_rank_value_checks": rank_comparisons,
    "exact_rational_kappa_checks": exact_kappa_checks,
    "numpy_version": np.__version__,
    "scipy_version": scipy.__version__,
    "kappa_definition": "1 - paired mean rank-distance penalty / mean penalty under the product of empirical rank marginals; distance exponent 1 or 2. Average ranks retain half-rank spacing. Ordinal ties use stable policy-ID order.",
    "scope": "Point estimates for this complete declared model, retaining all predeclared analysis choices. Not original-author settings, uncertainty-bar reproduction, whole-experiment completion, or a validated negative replication.",
    "sha256": {
        "model_audit": hashlib.sha256(
            (args.model_audit / "audit.json").read_bytes()
        ).hexdigest(),
        "reference_audit": hashlib.sha256(published.read_bytes()).hexdigest(),
        **{
            name: hashlib.sha256((args.output / name).read_bytes()).hexdigest()
            for name in ["rankings.csv", "objective-totals.csv"]
        },
    },
}
(args.output / "analysis.json").write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps(report))
