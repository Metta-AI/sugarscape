"""Analyze every published seasonal seed without selecting favorable windows."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("observed", type=Path)
parser.add_argument("output", type=Path)
args = parser.parse_args()
manifest = json.loads((args.observed / "manifest.json").read_text())
completed = [json.loads(line) for line in (args.observed / "completed.jsonl").read_text().splitlines()]
assert [r["seed"] for r in completed] == manifest["seeds"]
assert len(completed) == 20
assert all(r["result"]["native_trajectory_byte_identical"] for r in completed)
root = Path(__file__).resolve().parent
published = json.loads((root / "published_targets.json").read_text())
assert manifest["seeds"] == [r["seed"] for r in published["table3"]]
args.output.mkdir(parents=True, exist_ok=False)
summary = []
for seed in manifest["seeds"]:
    output = args.output / f"seed-{seed}"
    with (args.output / f"seed-{seed}.log").open("x") as log:
        subprocess.run([sys.executable, str(root / "analyze_seasons.py"),
                        str(args.observed / f"seed-{seed}"), str(output)],
                       stdout=log, stderr=subprocess.STDOUT, check=True)
    cohorts = json.loads((output / "cohorts.json").read_text())["cohorts"]
    assert [c["transition"] for c in cohorts] == list(range(50, 500, 50))
    groups = {}
    for category in ["groups", "migration_groups"]:
        for group in cohorts[0][category]:
            totals = {key: sum(c[category][group][key] for c in cohorts)
                      for key in ["count", "vision_sum", "sugar_metabolism_sum"]}
            assert totals["count"] > 0, "An empty group has no defined mean"
            groups[group] = {**totals, "mean_vision": totals["vision_sum"] / totals["count"],
                             "mean_sugar_metabolism": totals["sugar_metabolism_sum"] / totals["count"]}
    summary.append({"seed": seed, "cohorts": len(cohorts),
                    "cohort_memberships": sum(c["initial_cohort"] for c in cohorts),
                    "ever_crossed": sum(c["ever_crossed_to_wet_half"] for c in cohorts),
                    "ever_crossed_but_absent_at_end": sum(c["ever_crossed_but_absent_at_end"] for c in cohorts),
                    "groups": groups})
report = {"seeds": len(summary), "cohorts": sum(s["cohorts"] for s in summary),
          "observations": sum(r["result"]["observations"] for r in completed),
          "analyzer_sha256": hashlib.sha256((root / "analyze_seasons.py").read_bytes()).hexdigest(),
          "results": summary,
          "limitation": "Descriptive measures across nine seasonal windows per seed. Agents can occur in multiple cohorts; memberships are not independent observations. Absence can reflect natural lifespan, not just starvation. No causal or paper-replication verdict."}
(args.output / "summary.json").write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps(report))
