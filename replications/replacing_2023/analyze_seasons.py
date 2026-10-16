"""Measure seasonal cohorts from parity-verified individual observations."""
import argparse
import gzip
import hashlib
import json
from pathlib import Path

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("observed", type=Path)
parser.add_argument("output", type=Path)
args = parser.parse_args()
audit = json.loads((args.observed / "audit.json").read_text())
assert audit["native_trajectory_byte_identical"]
compressed = (args.observed / "observations.jsonl.gz").read_bytes()
assert hashlib.sha256(compressed).hexdigest() == audit["observations_sha256"]
rows = [json.loads(line) for line in gzip.decompress(compressed).splitlines()]
assert len(rows) == audit["observations"] == 501
assert [r["timestep"] for r in rows] == list(range(501))
occupancy = []
for row in rows:
    agents = row["agents"]
    assert len(agents) == row["population"]
    # The released source initializes seasons from y, then toggles every 50 steps.
    for a in agents:
        expected = "summer" if (a[2] >= 25) == (row["timestep"] // 50 % 2 == 0) else "winter"
        assert a[7] == expected
    occupancy.append({"timestep": row["timestep"], "population": len(agents),
                      "in_wet_half": sum(a[7] == "summer" for a in agents)})
cohorts = []
for transition in range(50, 500, 50):
    before = {a[0]: a for a in rows[transition - 1]["agents"] if a[7] == "summer"}
    after = {a[0]: a for a in rows[transition + 49]["agents"]}
    ever_crossed = {a[0] for row in rows[transition:transition + 50] for a in row["agents"]
                    if a[0] in before and a[7] == "summer"}
    groups = {"crossed_to_wet_half": [], "in_dry_half_at_end": [], "no_longer_present": []}
    for identity, agent in before.items():
        if identity not in after:
            groups["no_longer_present"].append(agent)
        elif after[identity][7] == "summer":
            groups["crossed_to_wet_half"].append(agent)
        else:
            groups["in_dry_half_at_end"].append(agent)
    assert sum(len(group) for group in groups.values()) == len(before)
    migration_groups = {"ever_crossed": [a for identity, a in before.items() if identity in ever_crossed],
                        "never_crossed": [a for identity, a in before.items() if identity not in ever_crossed]}
    cohorts.append({"transition": transition, "end": transition + 49, "initial_cohort": len(before),
                    "ever_crossed_to_wet_half": len(ever_crossed),
                    "ever_crossed_but_absent_at_end": len(ever_crossed - after.keys()),
                    "migration_groups": {name: {"count": len(group), "vision_sum": sum(a[3] for a in group),
                                                  "sugar_metabolism_sum": sum(a[4] for a in group)}
                                         for name, group in migration_groups.items()},
                    "groups": {name: {"count": len(group), "vision_sum": sum(a[3] for a in group),
                                     "sugar_metabolism_sum": sum(a[4] for a in group)} for name, group in groups.items()}})
report = {"observations": len(rows), "cohorts": cohorts,
          "coordinate_check": "Every observed cell season matches y-half and the native 50-step toggle; the x-based hemisphere label is not used.",
          "definition": "Track agents in the wet half immediately before each flip. Track any arrival in the newly wet half during the next 50 steps, including agents absent at the end. Separately partition end-of-window locations and absence. Replacement IDs never count as migrants.",
          "limitation": "Descriptive migration and survival measurements. Remaining in the dry half does not alone establish hibernation. No post-hoc paper similarity threshold."}
args.output.mkdir(parents=True, exist_ok=False)
(args.output / "cohorts.json").write_text(json.dumps(report, indent=2) + "\n")
(args.output / "occupancy.json").write_text(json.dumps(occupancy, indent=2) + "\n")
print(json.dumps(report))
