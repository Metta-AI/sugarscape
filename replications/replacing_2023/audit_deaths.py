"""Validate native death causes and reconcile every disappeared observed identity."""
import argparse
import gzip
import hashlib
import json
from pathlib import Path
import subprocess
import sys

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("baseline", type=Path)
parser.add_argument("observed", type=Path)
args = parser.parse_args()
subprocess.run([sys.executable, str(Path(__file__).with_name("audit_observation.py")),
                str(args.baseline), str(args.observed)], check=True)
trajectory = json.loads((args.baseline / "trajectory.json").read_text())
with gzip.open(args.observed / "observations.jsonl.gz", "rt") as stream:
    records = [json.loads(line) for line in stream]
previous_ids = set()
seen_deaths = set()
counts = {cause: 0 for cause in ["aging", "starvation", "combat", "disease"]}
for record, native in zip(records, trajectory, strict=True):
    agents = record["agents"]
    deaths = record["deaths"]
    death_ids = {d[0] for d in deaths}
    live_ids = {a[0] for a in agents}
    assert len(death_ids) == len(deaths)
    assert not death_ids & (live_ids | seen_deaths)
    assert previous_ids - live_ids <= death_ids
    assert all(len(d) == 6 and d[1] in {"aging", "starvation", "combat", "disease"} for d in deaths)
    assert all(d[2] >= d[3] and d[3] != -1 for d in deaths if d[1] == "aging")
    for cause, column in [("aging", "agentAgingDeaths"), ("starvation", "agentStarvationDeaths"),
                          ("combat", "agentCombatDeaths"), ("disease", "agentDiseaseDeaths")]:
        assert sum(d[1] == cause for d in deaths) == native[column]
    previous_ids = live_ids
    seen_deaths.update(death_ids)
    for death in deaths:
        counts[death[1]] += 1
report = {"observations": len(records), "death_records": len(seen_deaths),
          "death_counts_match_native": True, "causes": counts,
          "observations_sha256": hashlib.sha256((args.observed / "observations.jsonl.gz").read_bytes()).hexdigest()}
(args.observed / "death-audit.json").write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps(report))
