"""Summarize every audited published seasonal seed without pooling survival causes."""
import argparse
import hashlib
import json
from pathlib import Path

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("observed", type=Path)
parser.add_argument("cohorts", type=Path)
parser.add_argument("output", type=Path)
args = parser.parse_args()
root = Path(__file__).resolve().parent
seeds = [r["seed"] for r in json.loads((root / "published_targets.json").read_text())["table3"]]
completed = [json.loads(line) for line in (args.observed / "completed.jsonl").read_text().splitlines()]
assert [r["seed"] for r in completed] == seeds
results = []
for seed in seeds:
    observed = args.observed / f"seed-{seed}"
    audit = json.loads((observed / "death-audit.json").read_text())
    data = json.loads((args.cohorts / f"seed-{seed}/death-cohorts.json").read_text())
    checksum = hashlib.sha256((observed / "observations.jsonl.gz").read_bytes()).hexdigest()
    assert checksum == audit["observations_sha256"] == data["observations_sha256"]
    assert audit["death_counts_match_native"] and audit["observations"] == 501
    assert [c["transition"] for c in data["cohorts"]] == list(range(50, 500, 50))
    outcomes = {cause: sum(g["count"] for c in data["cohorts"] for g in c["groups"] if g["outcome"] == cause)
                for cause in ["survived", "aging", "starvation", "combat", "disease"]}
    memberships = sum(c["memberships"] for c in data["cohorts"])
    assert sum(outcomes.values()) == memberships
    results.append({"seed": seed, "memberships": memberships, "outcomes": outcomes,
                    "full_run_deaths": audit["causes"]})
report = {"seeds": len(seeds), "observations": 501 * len(seeds), "cohorts": 9 * len(seeds),
          "results": results,
          "cohort_totals": {cause: sum(r["outcomes"][cause] for r in results) for cause in outcomes},
          "limitation": "Cohort memberships can repeat identities across windows. Native proximate cause labels do not establish causal effects of seasons. Full-run deaths include replacements outside original cohorts."}
args.output.mkdir(parents=True, exist_ok=False)
(args.output / "summary.json").write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps(report))
