"""Summarize one original selfishness condition only after all 500 seeds pass audit."""

import argparse
from collections import Counter
from decimal import Decimal
import hashlib
import json
from pathlib import Path
import zipfile

from run_supplement import ARCHIVE_SHA256, RELEASE

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("archive", type=Path)
parser.add_argument("inventory", type=Path)
parser.add_argument("condition", type=int, choices=range(101))
parser.add_argument("output", type=Path)
args = parser.parse_args()
assert not args.output.exists()
assert (
    hashlib.sha256(args.archive.read_bytes()).hexdigest()
    == ARCHIVE_SHA256["selfishness"]
)
inventory = json.loads(args.inventory.read_bytes())
assert inventory["release"] == RELEASE
expected = {}
with zipfile.ZipFile(args.archive) as archive:
    for name in archive.namelist():
        raw = archive.read(name)
        config = json.loads(raw)
        factor = config["agentSelfishnessFactor"]
        if Decimal(str(factor[0])) * 100 != args.condition:
            continue
        assert factor == [factor[0], factor[0]]
        assert config["startingAgents"] == 250 and config["timesteps"] == 5000
        assert config["agentDecisionModel"] == "benthamHalfLookaheadBinary"
        assert name not in expected
        expected[name] = {
            "seed": config["seed"],
            "sha256": hashlib.sha256(raw).hexdigest(),
        }
assert len(expected) == len({row["seed"] for row in expected.values()}) == 500
selected = [
    row
    for row in inventory["excluded_controls"]
    if row["experiment"] == "selfishness" and row["entry"] in expected
]
assert len(selected) == len({row["entry"] for row in selected}), (
    "Duplicate input identity"
)
missing = sorted(expected.keys() - {row["entry"] for row in selected})
assert not missing, {
    "validated_inputs": len(selected),
    "required_inputs": 500,
    "missing_inputs": len(missing),
    "first_missing": missing[:5],
}
archive_hashes = {
    row["native_archive"]: row["native_archive_sha256"]
    for row in inventory["completed_sources"]
}
verified_archives = {}
results = []
for item in sorted(selected, key=lambda row: row["entry"]):
    target = expected[item["entry"]]
    assert item["configuration_sha256"] == target["sha256"]
    assert item["audit_sources"]
    repeated = []
    for source in item["audit_sources"]:
        path = Path(source["audit"])
        raw = path.read_bytes()
        assert hashlib.sha256(raw).hexdigest() == source["audit_sha256"]
        archive_path = source["native_archive"]
        if archive_path not in verified_archives:
            digest = hashlib.sha256(Path(archive_path).read_bytes()).hexdigest()
            assert digest == archive_hashes[archive_path]
            verified_archives[archive_path] = digest
        result = json.loads(raw)["validated"]
        assert (
            result["entry"] == item["entry"] and result["experiment"] == "selfishness"
        )
        assert result["seed"] == target["seed"]
        assert result["trajectory_sha256"] == item["trajectory_sha256"]
        assert result["observations"] == result["final_timestep"] + 1
        assert result["final_timestep"] == 5000 or result["final_population"] == 0
        population = result["final_population"]
        assert 0 <= population <= 2500
        category = (
            "dead"
            if population == 0
            else "worse"
            if population < 250
            else "better_or_equal"
        )
        assert result["outcome"] == category
        repeated.append(result)
    assert all(row == repeated[0] for row in repeated)
    results.append(repeated[0])
counts = Counter(row["outcome"] for row in results)
report = {
    "condition_hundredths": args.condition,
    "validated_inputs": 500,
    "counts": {name: counts[name] for name in ["dead", "worse", "better_or_equal"]},
    "observations": sum(row["observations"] for row in results),
    "inventory_sha256": hashlib.sha256(args.inventory.read_bytes()).hexdigest(),
    "source_archive_sha256": ARCHIVE_SHA256["selfishness"],
    "native_archive_sha256": verified_archives,
    "results": results,
    "scope": "Complete original condition endpoint counts from independently audited evidence. No paper-figure agreement, sweep completion, or whole-paper verdict is inferred.",
}
args.output.mkdir(parents=True)
(args.output / "summary.json").write_text(json.dumps(report, indent=2) + "\n")
print(
    json.dumps(
        {
            key: value
            for key, value in report.items()
            if key not in ["results", "native_archive_sha256"]
        }
    )
)
