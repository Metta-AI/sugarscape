"""Compare complete paired ensembles differing only in their printed death rule."""

import argparse
import csv
import hashlib
import json
from pathlib import Path

import numpy as np

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("original", type=Path)
parser.add_argument("changed", type=Path)
parser.add_argument("original_audits", type=Path)
parser.add_argument("changed_audits", type=Path)
parser.add_argument("output", type=Path)
args = parser.parse_args()
old_protocol = json.loads((args.original / "protocol.json").read_text())
new_protocol = json.loads((args.changed / "protocol.json").read_text())
assert (
    new_protocol["paired_reference_protocol_sha256"]
    == hashlib.sha256((args.original / "protocol.json").read_bytes()).hexdigest()
)
assert old_protocol["seed_generation"] == new_protocol["seed_generation"]
assert old_protocol["policies_sha256"] == new_protocol["policies_sha256"]
for old, new in zip(old_protocol["jobs"], new_protocol["jobs"], strict=True):
    assert {k: v for k, v in old.items() if k != "model_sha256"} == {
        k: v for k, v in new.items() if k != "model_sha256"
    }
rows = []
audit_hashes = {}
for model in sorted({job["model"] for job in new_protocol["jobs"]}):
    original_model = (args.original / model / "oremland.nlogo").read_text()
    assert original_model.count("ask turtles with [sugar <= 0] [die]") == 1
    assert (
        args.changed / model / "oremland.nlogo"
    ).read_text() == original_model.replace(
        "ask turtles with [sugar <= 0] [die]", "ask turtles with [sugar < 0] [die]"
    )
    values = []
    for directory, protocol in [
        (args.original_audits, args.original),
        (args.changed_audits, args.changed),
    ]:
        audit_path = directory / model / "audit.json"
        audit = json.loads(audit_path.read_text())
        audit_hashes[str(audit_path)] = hashlib.sha256(
            audit_path.read_bytes()
        ).hexdigest()
        assert (
            audit["protocol_sha256"]
            == hashlib.sha256((protocol / "protocol.json").read_bytes()).hexdigest()
        )
        objectives = directory / model / "objectives.npz"
        assert (
            audit["objectives_npz_sha256"]
            == hashlib.sha256(objectives.read_bytes()).hexdigest()
        )
        with np.load(objectives) as archive:
            values.append(archive["objectives"])
    before, after = values
    assert before.shape == after.shape
    for phase_index, phase in enumerate([0, 4]):
        for metric_index, metric in enumerate(["deaths", "literal_revenue"]):
            a = before[:, phase_index, :, metric_index].ravel()
            b = after[:, phase_index, :, metric_index].ravel()
            delta = b - a
            rows.append(
                {
                    "model": model,
                    "phase": phase,
                    "metric": metric,
                    "paired_runs": len(a),
                    "changed_runs": int(np.count_nonzero(delta)),
                    "prose_mean": float(a.mean()),
                    "algorithm_mean": float(b.mean()),
                    "mean_paired_change": float(delta.mean()),
                    "minimum_paired_change": int(delta.min()),
                    "maximum_paired_change": int(delta.max()),
                }
            )
args.output.mkdir(parents=True, exist_ok=False)
with (args.output / "paired-comparison.csv").open("w") as stream:
    writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
    writer.writeheader()
    writer.writerows(rows)
(args.output / "audit.json").write_text(
    json.dumps(
        {
            "paired_native_runs": sum(
                row["paired_runs"] for row in rows if row["metric"] == "deaths"
            ),
            "input_audits_sha256": audit_hashes,
            "scope": "Descriptive paired source-rule sensitivity. Neither rule establishes author-code fidelity or paper replication.",
        },
        indent=2,
    )
    + "\n"
)
