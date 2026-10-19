"""Extend audited runtime coverage, verifying every overlapping original input."""

import argparse
from collections import defaultdict
import hashlib
import json
from pathlib import Path
import zipfile

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("archive", type=Path)
parser.add_argument("previous", type=Path)
parser.add_argument("output", type=Path)
parser.add_argument("audits", nargs="+", type=Path)
args = parser.parse_args()
assert (
    hashlib.sha256(args.archive.read_bytes()).hexdigest()
    == "43b1967e9af9d7aac9785258706fd5abec6257235940b85aa811519c0e6ae98a"
)
with zipfile.ZipFile(args.archive) as z:
    configs = {n: json.loads(z.read(n)) for n in z.namelist() if n.endswith(".config")}
assert len(configs) == 1200
previous = json.loads(args.previous.read_text())
records = {}
sources = []
keys = [
    "entry",
    "seed",
    "observations",
    "final_population",
    "final_timestep",
    "outcome",
    "trajectory_sha256",
]
old_count = old_observations = 0
inputs = [(Path(s["path"]), s["sha256"]) for s in previous["source_audits"]]
inputs += [(p, hashlib.sha256(p.read_bytes()).hexdigest()) for p in args.audits]
for index, (path, digest) in enumerate(inputs):
    content = path.read_bytes()
    assert hashlib.sha256(content).hexdigest() == digest
    audit = json.loads(content)
    for row in audit["results"]:
        record = {k: row[k] for k in keys}
        entry = row["entry"]
        assert entry in configs and configs[entry]["seed"] == row["seed"]
        assert row["final_timestep"] <= configs[entry]["timesteps"]
        if entry in records:
            assert records[entry] == record, entry
        else:
            records[entry] = record
    sources.append(
        {"path": str(path), "sha256": digest, "records": len(audit["results"])}
    )
    if index + 1 == len(previous["source_audits"]):
        old_count = len(records)
        old_observations = sum(r["observations"] for r in records.values())
        assert old_count == previous["unique_inputs"]
        assert old_observations == previous["observations"]
groups = defaultdict(list)
for entry, config in configs.items():
    group = (config["agentDecisionModels"][0], config["timesteps"])
    groups[group].append(entry)
assert len(groups) == 12 and all(len(v) == 100 for v in groups.values())
report = {
    "unique_inputs": len(records),
    "required_inputs": 1200,
    "observations": sum(r["observations"] for r in records.values()),
    "new_since_published": {
        "inputs": len(records) - old_count,
        "observations": sum(r["observations"] for r in records.values())
        - old_observations,
    },
    "groups": [
        {
            "model": model,
            "steps": steps,
            "validated_runs": sum(e in records for e in entries),
            "complete_original_group": all(e in records for e in entries),
            "observations": sum(
                records[e]["observations"] for e in entries if e in records
            ),
        }
        for (model, steps), entries in sorted(groups.items())
    ],
    "source_audits": sources,
    "deduplication": previous["deduplication"],
    "scope": previous["scope"],
}
args.output.mkdir(parents=True, exist_ok=False)
(args.output / "coverage.json").write_text(json.dumps(report, indent=2) + "\n")
print(
    json.dumps(
        {k: v for k, v in report.items() if k not in ["groups", "source_audits"]}
    )
)
