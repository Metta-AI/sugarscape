"""Verify passive trace parity and summarize shared-resource debt events."""

import argparse
import csv
import hashlib
import json
import math
from pathlib import Path

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("reference", type=Path)
parser.add_argument("trace", type=Path)
parser.add_argument("output", type=Path)
args = parser.parse_args()
parity = {}
for name in ["accounting.csv", "health.csv", "prices.json", "complete.json"]:
    data = (args.reference / name).read_bytes()
    assert data == (args.trace / "run" / name).read_bytes(), name
    parity[name] = hashlib.sha256(data).hexdigest()
assert json.loads((args.trace / "run/complete.json").read_text())["steps"] == 1000
events = [
    json.loads(line) for line in (args.trace / "events.jsonl").read_text().splitlines()
]
for event in events:
    assert 1 <= event["step"] <= 1000
    assert event["agent"] in event["shared_members"]
    assert event["status"] == "alive"
    assert all(
        math.isfinite(value) for key in ["before", "after"] for value in event[key]
    )
    if event["event"] == "negative_after_metabolism":
        assert min(event["after"]) < 0
        assert all(a < b for a, b in zip(event["after"], event["before"]))
    else:
        assert event["event"] == "harvest_with_existing_debt"
        assert min(event["before"]) < 0
        assert all(a >= b for a, b in zip(event["after"], event["before"]))
shared_debt = [
    e
    for e in events
    if e["event"] == "negative_after_metabolism" and len(e["shared_members"]) > 1
]
recovery = [
    e
    for e in events
    if e["event"] == "harvest_with_existing_debt" and min(e["after"]) > 0.1
]
health = list(csv.DictReader((args.reference / "health.csv").open()))
negative = [
    r for r in health if min(float(r[k]) for k in ["Sugar_Level", "Spice_Level"]) < 0
]
summary = {
    "parity_sha256": parity,
    "events_sha256": hashlib.sha256(
        (args.trace / "events.jsonl").read_bytes()
    ).hexdigest(),
    "events": len(events),
    "shared_debt_metabolism_events": len(shared_debt),
    "harvest_restores_both_above_death_threshold": len(recovery),
    "negative_end_step_health_records": len(negative),
    "first_shared_debt": shared_debt[0],
    "first_harvest_recovery": recovery[0],
    "interpretation": "Harvest can restore a negative shared balance before the native pre-metabolism death check. This is observed corrective-model behavior, not a paper-level replication verdict.",
}
args.output.mkdir(parents=True, exist_ok=False)
(args.output / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
print(json.dumps(summary, indent=2))
