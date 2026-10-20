"""Reconcile complete endpoint controls against the frozen original-input partition."""

from collections import Counter
import gzip
import hashlib
import json
from pathlib import Path
import sys

workspace, output = map(Path, sys.argv[1:])
assert not output.exists()
evidence = workspace / "sugarscape-replication-evidence"
study = workspace / "sugarscape-need-for-greed/replications/need_for_greed_2024/results"
paths = {
    "baseline": study / "baseline-reuse-2026-10-19/native-audit.json",
    "sweep": study / "selfishness037-reuse-2026-10-19/audit.json",
    "controls": evidence / "need-for-greed-endpoint-recovery-001/audit.json",
    "plan": evidence / "need-for-greed-remaining-plan-001/prepared/plan.json",
    "inputs": evidence / "need-for-greed-remaining-plan-001/prepared/inputs.json.gz",
}
raw = {name: path.read_bytes() for name, path in paths.items()}
hashes = {name: hashlib.sha256(data).hexdigest() for name, data in raw.items()}
documents = {name: json.loads(data) for name, data in raw.items() if name != "inputs"}
assert hashes["inputs"] == documents["plan"]["inputs_json_gz_sha256"]
assert hashes["baseline"] == documents["plan"]["source_sha256"]["baseline"]
assert hashes["sweep"] == documents["plan"]["source_sha256"]["sweep"]
assert (
    documents["controls"]["protocol_sha256"]
    == documents["plan"]["source_sha256"]["controls"]
)
inputs = json.loads(gzip.decompress(raw["inputs"]))
assert len(inputs) == len({row["entry"] for row in inputs}) == 10500
prior = documents["baseline"]["runs"] + documents["sweep"]["runs"]
controls = documents["controls"]["runs"]
assert len(prior) == len({row["entry"] for row in prior}) == 164
assert len(controls) == len({row["entry"] for row in controls}) == 6
prior_names = {row["entry"] for row in prior}
control_names = {row["entry"] for row in controls}
assert prior_names.isdisjoint(control_names)
assert prior_names == {
    row["entry"] for row in inputs if row["disposition"] == "audited"
}
assert control_names == {
    row["entry"] for row in inputs if row["disposition"] == "reserved_control"
}
for row in inputs:
    if row["entry"] in control_names:
        row["disposition"] = "audited"
counts = Counter((row["kind"], row["disposition"]) for row in inputs)
reports = prior + controls
assert sum(row["observations"] for row in reports) == 835607
report = {
    "source_sha256": hashes,
    "partition_counts": {
        kind: {
            state: counts[kind, state]
            for state in ("audited", "reserved_control", "remaining")
        }
        for kind in ("baseline", "sweep")
    },
    "audited_inputs": len(reports),
    "audited_observations": sum(row["observations"] for row in reports),
    "new_inputs": len(controls),
    "new_observations": sum(row["observations"] for row in controls),
    "overlap": [],
    "runs": [
        {
            key: row[key]
            for key in (
                "entry",
                "observations",
                "trajectory_sha256",
                "final_population",
            )
        }
        for row in reports
    ],
    "scope": "Coverage reconciliation of previously audited artifacts and six freshly audited controls. Does not rerun prior artifact auditors or establish all-seed equivalence. The 400-input cloud batch remains uncredited. No paper completion credit.",
}
output.write_text(json.dumps(report, indent=2) + "\n")
print(
    json.dumps({key: value for key, value in report.items() if key != "runs"}, indent=2)
)
