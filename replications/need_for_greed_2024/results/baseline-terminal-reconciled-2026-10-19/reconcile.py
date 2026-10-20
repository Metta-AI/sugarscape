"""Reconcile every terminal attempt, deduplicate prior prefix, and freeze unfinished inputs."""

from pathlib import Path
import hashlib
import json

root = Path(__file__).resolve().parent
base = root.parent
previous = json.loads(
    (base / "need-for-greed-table4-prefix-001/reconciliation.json").read_bytes()
)
audits = [json.loads((root / f"audit-{i}.json").read_bytes()) for i in (1, 2)]
producer = json.loads((root / "producer-terminal.json").read_bytes())
plan = json.loads(
    (base / "need-for-greed-baseline-recovery-001/payload/plan.json").read_bytes()
)
completed = [r for a in audits for r in a["runs"]]
failed = [r for a in audits for r in a["failures"]]
assert len(completed) == len({r["entry"] for r in completed}) == 40
assert len(failed) == 1
assert {r["entry"] for r in completed} == {
    r["entry"] for r in producer["records"] if r["verified"]
}
assert {r["entry"] for r in failed} == {
    r["entry"] for r in producer["records"] if not r["verified"]
}
assert producer["verified_inputs"] == 40 and len(producer["records"]) == 41
old = {r["entry"]: r for r in previous["runs"]}
overlap = []
added = []
for row in completed:
    if row["entry"] in old:
        assert row == old[row["entry"]]
        overlap.append(row["entry"])
    else:
        old[row["entry"]] = row
        added.append(row["entry"])
assert len(overlap) == 22 and len(added) == 18 and len(old) == 237
remaining = [
    r for r in plan["rows"] if r["entry"] not in {x["entry"] for x in completed}
]
assert len(remaining) == 293 and {r["entry"] for r in remaining} == set(
    producer["remaining"]
)
assert {r["entry"] for r in remaining}.isdisjoint(old)
report = {
    "audited_inputs": len(old),
    "audited_observations": sum(r["observations"] for r in old.values()),
    "new_inputs": 18,
    "new_observations": sum(old[e]["observations"] for e in added),
    "overlapping_verified_inputs": overlap,
    "runs": list(old.values()),
    "failures": failed,
    "partition_counts": {
        "baseline": {"audited": 107, "remaining": 293},
        "sweep": {"audited": 130, "remaining": 9970},
    },
    "remaining_original_rows": remaining,
    "producer_terminal_sha256": hashlib.sha256(
        (root / "producer-terminal.json").read_bytes()
    ).hexdigest(),
    "scope": "Complete terminal attempt accounting. Failed partial output excluded. Remaining293original baseline inputs include1failed and292unstarted; not authorized for automatic retry by the old batch.",
}
(root / "reconciliation.json").write_text(json.dumps(report, indent=2) + "\n")
print(
    json.dumps(
        {
            k: v
            for k, v in report.items()
            if k
            not in ("runs", "overlapping_verified_inputs", "remaining_original_rows")
        }
    )
)
