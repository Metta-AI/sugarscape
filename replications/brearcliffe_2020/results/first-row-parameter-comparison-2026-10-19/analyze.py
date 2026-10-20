"""Compare both frozen interpretations against the same corrected paper targets."""

from collections import Counter
import gzip
import hashlib
import json
from pathlib import Path
import sys

results, output = map(Path, sys.argv[1:])
assert not output.exists()
target = results / "horizontal-calibration-correction-2026-10-19/metric-curves.json.gz"
target_hash = hashlib.sha256(target.read_bytes()).hexdigest()
assert target_hash == "4ec231b3714289deeab9e92bae99efb3fe4c0cb2552e6ba2e7fd2565a12bc8fd"
pins = {str(target.relative_to(results)): target_hash}
reports = []
for pair, (released_name, paper_name) in enumerate(
    [
        ("rule-m-rule-m", "paper-rule-m"),
        ("rule-m-ec", "paper-rule-m-ec"),
        ("rule-m-q", "paper-rule-m-q"),
        ("rule-m-sarsa", "paper-rule-m-sarsa"),
    ]
):
    summaries = []
    comparisons = []
    for interpretation, name in (
        ("released-code", released_name),
        ("paper-table", paper_name),
    ):
        cohort = results / f"{name}-complete-cohort-2026-10-19"
        summary_path = cohort / "cohort-summary.json"
        means_path = cohort / "means.csv.gz"
        comparison_path = (
            results
            / "horizontal-calibration-correction-2026-10-19"
            / name
            / "curve-comparison.json.gz"
            if interpretation == "released-code"
            else cohort / "curve-comparison.json.gz"
        )
        for path in (summary_path, means_path, comparison_path):
            pins[str(path.relative_to(results))] = hashlib.sha256(
                path.read_bytes()
            ).hexdigest()
        summary = json.loads(summary_path.read_bytes())
        comparison = json.loads(gzip.decompress(comparison_path.read_bytes()))
        assert summary["pair_index"] == pair and summary["runs"] == 50
        assert (
            summary["interpretation"] == comparison["interpretation"] == interpretation
        )
        assert (
            comparison["summary_sha256"] == pins[str(summary_path.relative_to(results))]
        )
        assert (
            comparison["means_sha256"]
            == hashlib.sha256(gzip.decompress(means_path.read_bytes())).hexdigest()
        )
        assert comparison["curves_sha256"] == target_hash
        summaries.append(summary)
        comparisons.append(comparison)
    a, b = summaries
    assert a["manifest_sha256"] == b["manifest_sha256"]
    identical = sum(
        a["trajectory_sha256"][f"released-code-pair-{pair:02d}-repeat-{repeat:02d}"]
        == b["trajectory_sha256"][f"paper-table-pair-{pair:02d}-repeat-{repeat:02d}"]
        for repeat in range(50)
    )
    counts = Counter()
    endpoint_counts = Counter()
    endpoints = []
    ra, rb = [c["records"] for c in comparisons]
    assert len(ra) == len(rb) == 3876
    endpoint_columns = {
        s["metric"]: max(r["column"] for r in ra if r["metric"] == s["metric"])
        for s in a["endpoint_statistics"]
    }
    for x, y in zip(ra, rb, strict=True):
        assert {
            k: v
            for k, v in x.items()
            if k
            not in ("cohort_mean_range_over_tick_interval", "signed_range_separation")
        } == {
            k: v
            for k, v in y.items()
            if k
            not in ("cohort_mean_range_over_tick_interval", "signed_range_separation")
        }
        if "signed_range_separation" not in x:
            category = "unresolved"
        else:
            overlaps = (
                x["signed_range_separation"] == 0,
                y["signed_range_separation"] == 0,
            )
            category = {
                (True, True): "both_overlap",
                (True, False): "released_only",
                (False, True): "paper_only",
                (False, False): "neither_overlap",
            }[overlaps]
        counts[category] += 1
        if x["column"] == endpoint_columns[x["metric"]]:
            endpoint_counts[category] += 1
            sa = next(s for s in a["endpoint_statistics"] if s["metric"] == x["metric"])
            sb = next(s for s in b["endpoint_statistics"] if s["metric"] == x["metric"])
            endpoints.append(
                {
                    "metric": x["metric"],
                    "category": category,
                    "released_mean": sa["mean"],
                    "paper_mean": sb["mean"],
                    "paper_minus_released_mean": sb["mean"] - sa["mean"],
                }
            )
    assert sum(endpoint_counts.values()) == len(endpoints) == 14
    reports.append(
        {
            "pair_index": pair,
            "group_A": a["group_A"],
            "group_B": a["group_B"],
            "paired_inputs": 50,
            "identical_full_trajectories": identical,
            "curve_counts": dict(counts),
            "endpoint_counts": dict(endpoint_counts),
            "endpoints": endpoints,
        }
    )
report = {
    "source_sha256": pins,
    "paired_inputs": 200,
    "interpretation_inputs": 400,
    "pairings": reports,
    "scope": "Post hoc descriptive comparison of four complete paired cohorts, using identical corrected targets. Adjacent columns are dependent. No parameter selection, historical identification, equivalence test, additional simulation coverage, or whole-paper verdict.",
}
output.write_text(json.dumps(report, indent=2) + "\n")
print(
    json.dumps(
        [{k: v for k, v in r.items() if k != "endpoints"} for r in reports], indent=2
    )
)
