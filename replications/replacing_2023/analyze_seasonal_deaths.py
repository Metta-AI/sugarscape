"""Attribute seasonal cohort disappearance to parity-verified native death causes."""
import argparse
import gzip
import hashlib
import json
from pathlib import Path

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("observed", type=Path)
parser.add_argument("output", type=Path)
args = parser.parse_args()
audit = json.loads((args.observed / "death-audit.json").read_text())
data = (args.observed / "observations.jsonl.gz").read_bytes()
assert hashlib.sha256(data).hexdigest() == audit["observations_sha256"]
assert audit["death_counts_match_native"]
rows = [json.loads(line) for line in gzip.decompress(data).splitlines()]
assert [r["timestep"] for r in rows] == list(range(501))
cohorts = []
for transition in range(50, 500, 50):
    before = {a[0]: a for a in rows[transition - 1]["agents"] if a[7] == "summer"}
    window = rows[transition:transition + 50]
    crossed = {a[0] for row in window for a in row["agents"] if a[0] in before and a[7] == "summer"}
    deaths = {d[0]: d[1] for row in window for d in row["deaths"] if d[0] in before}
    survivors = {a[0] for a in window[-1]["agents"]} & before.keys()
    assert deaths.keys() | survivors == before.keys()
    assert not deaths.keys() & survivors
    groups = []
    for migrated in [False, True]:
        for outcome in ["survived", "aging", "starvation", "combat", "disease"]:
            identities = survivors if outcome == "survived" else {identity for identity, cause in deaths.items() if cause == outcome}
            agents = [before[identity] for identity in identities if (identity in crossed) == migrated]
            groups.append({"migrated": migrated, "outcome": outcome, "count": len(agents),
                           "initial_vision_sum": sum(a[3] for a in agents),
                           "initial_metabolism_sum": sum(a[4] for a in agents)})
    assert sum(g["count"] for g in groups) == len(before)
    cohorts.append({"transition": transition, "memberships": len(before), "groups": groups})
report = {"cohorts": cohorts, "observations_sha256": audit["observations_sha256"],
          "limitation": "Native cause labels identify proximate deaths, not the causal effect of seasons. Memberships across windows are dependent. Migration requires an observed live arrival and excludes replacement identities."}
args.output.mkdir(parents=True, exist_ok=False)
(args.output / "death-cohorts.json").write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps(report))
