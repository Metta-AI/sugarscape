"""Verify passive movement-policy parity and audit each high-focus selection."""

import argparse
import hashlib
import json
from pathlib import Path

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("native", type=Path)
parser.add_argument("trace", type=Path)
parser.add_argument("output", type=Path)
parser.add_argument(
    "--highest", action="store_true", help="Require corrected highest-holding selection"
)
args = parser.parse_args()
parity = {}
for name in [
    "initial-agents.json",
    "observations.json",
    "health.csv",
    "population.csv",
    "prices.json",
]:
    data = (args.native / "run" / name).read_bytes()
    assert data == (args.trace / "configured/run" / name).read_bytes(), name
    parity[name] = hashlib.sha256(data).hexdigest()
assert json.loads((args.native / "run/complete.json").read_text())["steps"] == 1000
assert (
    json.loads((args.trace / "configured/run/complete.json").read_text())["steps"]
    == 1000
)
raw = (args.trace / "high-focus.jsonl").read_bytes()
events = [json.loads(line) for line in raw.splitlines()]
assert events
mismatches = []
for event in events:
    members = event["members_before_policy"]
    assert len(members) >= 2
    selector = max if args.highest else min
    selected = selector(
        members, key=lambda member: max(member["sugar"], member["spice"])
    )
    assert [event["perceived_sugar"], event["perceived_spice"]] == [
        selected["sugar"],
        selected["spice"],
    ]
    maximum = max(max(member["sugar"], member["spice"]) for member in members)
    if max(event["perceived_sugar"], event["perceived_spice"]) < maximum:
        mismatches.append(event)
assert not mismatches if args.highest else mismatches
report = {
    "steps": 1000,
    "byte_parity": parity,
    "high_focus_calls": len(events),
    "selection_rule": "largest-member-maximum"
    if args.highest
    else "smallest-member-maximum",
    "calls_matching_selection_rule": len(events),
    "calls_below_largest_member_maximum": len(mismatches),
    "first_mismatch": mismatches[0] if mismatches else None,
    "trace_sha256": hashlib.sha256(raw).hexdigest(),
    "scope": "Whole-model parity and explicit member-selection audit. The correction and released policy remain distinct experiments; historical paper revision is unverified. No whole-paper verdict.",
}
args.output.mkdir(parents=True, exist_ok=False)
(args.output / "audit.json").write_text(json.dumps(report, indent=2) + "\n")
print(
    json.dumps(
        {
            key: report[key]
            for key in ["high_focus_calls", "calls_below_largest_member_maximum"]
        }
    )
)
