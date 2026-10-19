from pathlib import Path
import csv
import hashlib
import json

root = Path(__file__).resolve().parent
previous_path = (
    root.parent / "brearcliffe-paper-ec-q-snapshot-001/union-audit/audit.json"
)
assert (
    json.loads((previous_path.parent.parent / "analysis-terminal.json").read_text())[
        "exit_code"
    ]
    == 0
)
previous = json.loads(previous_path.read_text())
delta_path = root / "delta-audit/audit.json"
delta = json.loads(delta_path.read_text())
assert previous["manifest_sha256"] == delta["manifest_sha256"]
assert previous["completed_inputs"] == 1127 and delta["completed_inputs"] == 25
prior_ids = {r["run_id"] for r in previous["completed"]}
new_ids = {r["run_id"] for r in delta["completed"]}
assert new_ids == {f"released-code-pair-15-repeat-{i:02d}" for i in range(25, 50)}
assert prior_ids.isdisjoint(new_ids)
completed = previous["completed"] + delta["completed"]
assert len(completed) == len(prior_ids | new_ids) == 1152
manifest = root.parent / "brearcliffe-ensemble-preparation-001/manifest.csv"
assert hashlib.sha256(manifest.read_bytes()).hexdigest() == previous["manifest_sha256"]
with manifest.open() as stream:
    reader = csv.DictReader(stream)
    fields = reader.fieldnames
    rows = list(reader)
assert len(rows) == 1600
remaining = [row for row in rows if row["run_id"] not in prior_ids | new_ids]
assert len(remaining) == 448
out = root / "union-audit"
out.mkdir()
report = {
    "manifest_sha256": previous["manifest_sha256"],
    "completed_inputs": 1152,
    "remaining_inputs": 448,
    "observations": sum(r["observations"] for r in completed),
    "completed": completed,
    "scope": "Reconciled immutable prior audit with25new full-trajectory audits. No complete-cohort or paper verdict.",
}
assert report["observations"] == 23041152
(out / "audit.json").write_text(json.dumps(report, indent=2) + "\n")
with (out / "remaining.csv").open("w", newline="") as stream:
    writer = csv.DictWriter(stream, fieldnames=fields)
    writer.writeheader()
    writer.writerows(remaining)
(root / "reconciliation-verification.json").write_text(
    json.dumps(
        {
            "prior_audit_sha256": hashlib.sha256(
                previous_path.read_bytes()
            ).hexdigest(),
            "delta_audit_sha256": hashlib.sha256(delta_path.read_bytes()).hexdigest(),
            "prior_records_unchanged": 1127,
            "new_disjoint_inputs": 25,
            "completed_inputs": 1152,
            "observations": 23041152,
            "released_code": 800,
            "paper_table": 352,
            "scope": "No incomplete50-run cohort statistics emitted.",
        },
        indent=2,
    )
    + "\n"
)
print(json.dumps({k: v for k, v in report.items() if k != "completed"}))
