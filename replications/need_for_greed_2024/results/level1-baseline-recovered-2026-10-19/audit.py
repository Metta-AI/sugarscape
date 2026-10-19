"""Verify the recovered full baseline against its old hash and failed prefix."""

from pathlib import Path
import hashlib
import json
import math
import sys
import zipfile

base, output = map(Path, sys.argv[1:])
assert not output.exists()
run = base / "need-for-greed-endpoint-recovery-001/1.0-baseline"
failed = base / "need-for-greed-endpoint-qualification-001/1.0-baseline"
prior_raw = (
    base / "need-for-greed-retained-audit-reuse-001/inventory.json"
).read_bytes()
prior = json.loads(prior_raw)
manifest = json.loads((run / "manifest.json").read_text())
pins = json.loads(
    (
        base.parent
        / "sugarscape-need-for-greed/replications/need_for_greed_2024/source-sha256.json"
    ).read_text()
)["source_sha256"]
assert manifest["source_sha256"] == pins
assert {
    p.name: hashlib.sha256(p.read_bytes()).hexdigest()
    for p in (base.parent / "sugarscape-dtl-blueprints-reference").glob("*.py")
} == pins
terminal = json.loads((run / "terminal.json").read_text())
result = json.loads((run / "result.json").read_text())
assert terminal["exit_code"] == 0 and result["status"] == "complete"
assert json.loads((failed / "terminal.json").read_text())["exit_code"] == 124
original = (run / "original.config").read_bytes()
archive = base / "papers/need-for-greed.zip"
assert (
    hashlib.sha256(archive.read_bytes()).hexdigest()
    == manifest["archive_sha256"]
    == "e41c89ed31811b2d100c0a54f9c0110f0572a980b599e2417b2653b934fbe440"
)
with zipfile.ZipFile(archive) as z:
    assert original == z.read(manifest["entry"])
assert hashlib.sha256(original).hexdigest() == manifest["original_config_sha256"]
assert json.loads((run / "config.json").read_text()) == json.loads(original) | {
    "logfile": str(run / "trajectory.json")
}
raw = (run / "trajectory.json").read_bytes()
prefix = (failed / "trajectory.json").read_bytes()
assert raw.startswith(prefix)
records = json.loads(raw)
assert len(records) == 5001 and records[0]["population"] == 250
arrays = {"agentWealths", "agentTimesToLive", "agentTimesToLiveAgeLimited"}
for t, row in enumerate(records):
    assert row["timestep"] == t and row["seed"] == manifest["seed"]
    assert (
        0 <= row["population"] <= 2500 and int(row["population"]) == row["population"]
    )
    assert {k for k, v in row.items() if isinstance(v, list)} == arrays
    assert all(math.isfinite(v) for k, v in row.items() if k not in arrays)
    assert all(math.isfinite(v) for k in arrays for v in row[k])
previous = next(r for r in prior["runs"] if r["entry"] == manifest["entry"])
sha = hashlib.sha256(raw).hexdigest()
assert sha == previous["result"]["trajectory_sha256"] == result["trajectory_sha256"]
assert (
    records[-1]["population"]
    == previous["result"]["final_population"]
    == result["final_population"]
    == 1132
)
assert previous["result"]["observations"] == 5001
report = {
    "entry": manifest["entry"],
    "seed": manifest["seed"],
    "observations": 5001,
    "recorded_values": sum(len(r) for r in records),
    "final_population": 1132,
    "trajectory_sha256": sha,
    "prior_baseline_hash_equal": True,
    "failed_prefix_bytes": len(prefix),
    "failed_prefix_sha256": hashlib.sha256(prefix).hexdigest(),
    "failed_prefix_exact": True,
    "elapsed_seconds": terminal["elapsed_seconds"],
    "original_config_sha256": hashlib.sha256(original).hexdigest(),
    "prior_inventory_sha256": hashlib.sha256(prior_raw).hexdigest(),
    "scope": "Full original selfishness1 baseline recovered. One complete native trajectory matches earlier baseline hash and all original interrupted bytes. Paired sweep and six-control reconciliation remain pending; no completed-paper credit.",
}
output.write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps(report, indent=2))
