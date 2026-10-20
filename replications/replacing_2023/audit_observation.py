"""Require native trajectory parity before summarizing observational evidence."""
import argparse
import gzip
import hashlib
import json
from pathlib import Path

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("baseline", type=Path)
parser.add_argument("observed", type=Path)
args = parser.parse_args()
baseline = (args.baseline / "trajectory.json").read_bytes()
observed = (args.observed / "trajectory.json").read_bytes()
assert observed == baseline, "Observer changed the native trajectory"
trajectory = json.loads(baseline)
with gzip.open(args.observed / "observations.jsonl.gz", "rt") as stream:
    records = [json.loads(line) for line in stream]
assert len(records) == len(trajectory)
summary = []
for record, native in zip(records, trajectory, strict=True):
    assert record["timestep"] == native["timestep"]
    agents = record["agents"]
    assert len(agents) == record["population"] == native["population"]
    assert len({a[0] for a in agents}) == len(agents)
    assert all(len(a) == 9 and 0 <= a[1] < 50 and 0 <= a[2] < 50 and a[6] >= 0 for a in agents)
    summary.append({"timestep": record["timestep"], "population": len(agents),
                    "infected": sum(a[6] > 0 for a in agents),
                    "x_below_equator": sum(a[1] < 25 for a in agents),
                    "y_below_equator": sum(a[2] < 25 for a in agents),
                    "summer": sum(a[7] == "summer" for a in agents)})
result = {"native_trajectory_byte_identical": True, "observations": len(records),
          "trajectory_sha256": hashlib.sha256(observed).hexdigest(),
          "observations_sha256": hashlib.sha256((args.observed / "observations.jsonl.gz").read_bytes()).hexdigest(),
          "minimum_population": min(r["population"] for r in summary),
          "final_population": summary[-1]["population"],
          "final_infected": summary[-1]["infected"],
          "first_zero_infections": next((r["timestep"] for r in summary if r["infected"] == 0), None),
          "interpretation": "Observer parity verified; historical configuration and qualitative paper claims remain unvalidated."}
(args.observed / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
(args.observed / "audit.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps(result))
