import argparse, csv, hashlib, json, math
from collections import defaultdict
from pathlib import Path

p = argparse.ArgumentParser()
p.add_argument("native", type=Path)
p.add_argument("observed", type=Path)
p.add_argument("output", type=Path)
a = p.parse_args()
assert not a.output.exists()
assert json.loads((a.observed / "exit.json").read_text()) == {"exit_code": 0}
assert json.loads((a.native / "exit.json").read_text()) == {"exit_code": 0}
parity = {}
for name in ["population.csv", "prices.json"]:
    raw = (a.native / name).read_bytes()
    assert raw == (a.observed / name).read_bytes(), name
    parity[name] = hashlib.sha256(raw).hexdigest()
rows = json.loads((a.observed / "observations.json").read_text())
assert [r["step"] for r in rows] == list(range(1, 1001))
initial = json.loads((a.observed / "initial-agents.json").read_text())
previous = {r["id"] for r in initial}
assert len(previous) == 200
health = defaultdict(set)
health_rows = 0
with (a.observed / "health.csv").open() as f:
    for r in csv.DictReader(f):
        step = int(r["Step"])
        agent = int(r["Agent"])
        assert agent not in health[step]
        health[step].add(agent)
        health_rows += 1
        assert all(math.isfinite(float(r[k])) for k in ["Sugar_Level", "Spice_Level"])
for r in rows:
    ids = set(r["agent_ids"])
    assert len(ids) == len(r["agent_ids"]) == r["individual_agents"]
    assert ids <= previous and ids == health[r["step"]]
    previous = ids
assert set(health) == set(range(1, 1001))
report = {
    "native": str(a.native),
    "observed": str(a.observed),
    "byte_identical_outputs": parity,
    "observations": len(rows),
    "validated_health_rows": health_rows,
    "final_individual_agents": rows[-1]["individual_agents"],
    "final_native_reporter": rows[-1]["native_reporter"],
    "scope": "Whole-model observer parity, surviving identities, monotonic individual population and native health-record reconciliation. Native reporter may count groups; no paper replication verdict.",
}
a.output.mkdir()
(a.output / "audit.json").write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps(report))
