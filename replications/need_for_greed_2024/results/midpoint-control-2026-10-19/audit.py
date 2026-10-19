"""Verify the full native midpoint pair and its previously recorded baseline hash."""

from pathlib import Path
import hashlib
import json
import math
import sys
import zipfile

evidence, output = map(Path, sys.argv[1:])
assert not output.exists()
root = evidence / "need-for-greed-endpoint-qualification-001"
protocol_raw = (root / "protocol.json").read_bytes()
protocol = json.loads(protocol_raw)
prior_raw = (
    evidence / "need-for-greed-retained-audit-reuse-001/inventory.json"
).read_bytes()
prior = json.loads(prior_raw)
archive = evidence / "papers/need-for-greed.zip"
assert hashlib.sha256(archive.read_bytes()).hexdigest() == protocol["archive_sha256"]
assert {
    p.name: hashlib.sha256(p.read_bytes()).hexdigest()
    for p in Path(protocol["engine"]).glob("*.py")
} == protocol["source"]["source_sha256"]
reports = []
payloads = []
with zipfile.ZipFile(archive) as bundle:
    for row in protocol["runs"]:
        if row["level"] != "0.5":
            continue
        path = Path(row["directory"])
        original = (path / "original.config").read_bytes()
        assert original == bundle.read(row["entry"])
        assert hashlib.sha256(original).hexdigest() == row["original_sha256"]
        effective = (path / "config.json").read_bytes()
        assert hashlib.sha256(effective).hexdigest() == row["effective_sha256"]
        assert json.loads(effective) == json.loads(original) | {
            "logfile": str(path / "trajectory.json")
        }
        terminal = json.loads((path / "terminal.json").read_text())
        assert terminal["exit_code"] == 0 and terminal["entry"] == row["entry"]
        raw = (path / "trajectory.json").read_bytes()
        records = json.loads(raw)
        assert len(records) == 5001
        assert records[0]["population"] == 250
        for t, record in enumerate(records):
            assert record["timestep"] == t and record["seed"] == row["seed"]
            assert all(
                math.isfinite(value)
                for value in record.values()
                if isinstance(value, (int, float))
            )
        sha = hashlib.sha256(raw).hexdigest()
        if row["kind"] == "baseline":
            previous = next(r for r in prior["runs"] if r["entry"] == row["entry"])
            assert sha == previous["result"]["trajectory_sha256"]
            assert len(records) == previous["result"]["observations"]
            assert records[-1]["population"] == previous["result"]["final_population"]
        reports.append(
            {
                "entry": row["entry"],
                "kind": row["kind"],
                "seed": row["seed"],
                "observations": len(records),
                "recorded_values": sum(len(r) for r in records),
                "trajectory_sha256": sha,
                "original_sha256": row["original_sha256"],
                "elapsed_seconds": terminal["elapsed_seconds"],
                "final_population": records[-1]["population"],
            }
        )
        payloads.append(raw)
assert len(payloads) == 2 and payloads[0] == payloads[1]
report = {
    "runs": reports,
    "all_trajectory_bytes_equal": True,
    "prior_baseline_hash_equal": True,
    "protocol_sha256": hashlib.sha256(protocol_raw).hexdigest(),
    "prior_inventory_sha256": hashlib.sha256(prior_raw).hexdigest(),
    "scope": "Complete native 5000-step midpoint pair at original seed238165197779399277. All recorded trajectories match exactly, including the prior baseline hash. This does not prove all-seed equivalence, identify historical aggregation, or complete the paper. Other control reservations remain separate.",
}
output.write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps(report, indent=2))
