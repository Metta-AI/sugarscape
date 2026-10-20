"""Audit all six original endpoint controls, preserving timed-out prefixes."""

from pathlib import Path
import hashlib
import json
import math
import sys
import zipfile

base, output = map(Path, sys.argv[1:])
assert not output.exists()
original = base / "need-for-greed-endpoint-qualification-001"
recovery = base / "need-for-greed-endpoint-recovery-001"
assert json.loads((recovery / "terminal.json").read_text())["all_exit_zero"]
protocol_raw = (original / "protocol.json").read_bytes()
protocol = json.loads(protocol_raw)
prior_raw = (
    base / "need-for-greed-retained-audit-reuse-001/inventory.json"
).read_bytes()
prior = json.loads(prior_raw)
archive = Path(protocol["archive"])
assert hashlib.sha256(archive.read_bytes()).hexdigest() == protocol["archive_sha256"]
assert {
    p.name: hashlib.sha256(p.read_bytes()).hexdigest()
    for p in Path(protocol["engine"]).glob("*.py")
} == protocol["source"]["source_sha256"]
reports = []
pairs = {}
with zipfile.ZipFile(archive) as bundle:
    for row in protocol["runs"]:
        old = Path(row["directory"])
        old_receipt = json.loads((old / "terminal.json").read_text())
        assert old_receipt["entry"] == row["entry"]
        assert old_receipt["exit_code"] in (0, 124)
        selected = (
            old
            if old_receipt["exit_code"] == 0
            else recovery / (row["level"] + "-" + row["kind"])
        )
        receipt = json.loads((selected / "terminal.json").read_text())
        assert receipt["exit_code"] == 0
        config = (selected / "original.config").read_bytes()
        assert config == bundle.read(row["entry"])
        assert hashlib.sha256(config).hexdigest() == row["original_sha256"]
        assert json.loads((selected / "config.json").read_text()) == json.loads(
            config
        ) | {"logfile": str(selected / "trajectory.json")}
        raw = (selected / "trajectory.json").read_bytes()
        prefix = (old / "trajectory.json").read_bytes()
        assert raw.startswith(prefix), (
            "Recovered trajectory differs from the original completed prefix"
        )
        records = json.loads(raw)
        assert records[0]["population"] == 250
        assert records[-1]["timestep"] == 5000 or records[-1]["population"] == 0
        arrays = {"agentWealths", "agentTimesToLive", "agentTimesToLiveAgeLimited"}
        for t, record in enumerate(records):
            assert record["timestep"] == t and record["seed"] == row["seed"]
            assert (
                0 <= record["population"] <= 2500
                and int(record["population"]) == record["population"]
            )
            assert {k for k, v in record.items() if isinstance(v, list)} == arrays
            assert all(math.isfinite(v) for k, v in record.items() if k not in arrays)
            assert all(math.isfinite(v) for k in arrays for v in record[k])
        sha = hashlib.sha256(raw).hexdigest()
        if row["kind"] == "baseline":
            previous = next(r for r in prior["runs"] if r["entry"] == row["entry"])
            assert sha == previous["result"]["trajectory_sha256"]
            assert len(records) == previous["result"]["observations"]
            assert records[-1]["population"] == previous["result"]["final_population"]
        pairs.setdefault(row["level"], []).append(raw)
        reports.append(
            {
                "entry": row["entry"],
                "source": str(selected),
                "observations": len(records),
                "trajectory_sha256": sha,
                "final_population": records[-1]["population"],
                "original_exit_code": old_receipt["exit_code"],
                "original_bytes": len(prefix),
                "original_sha256": hashlib.sha256(prefix).hexdigest(),
                "original_prefix_exact": True,
                "recovered": selected != old,
            }
        )
assert len(reports) == 6 and len(pairs) == 3
assert all(len(pair) == 2 and pair[0] == pair[1] for pair in pairs.values())
report = {
    "runs": reports,
    "pairwise_trajectory_bytes_equal": True,
    "prior_baseline_hashes_equal": True,
    "observations": sum(r["observations"] for r in reports),
    "protocol_sha256": hashlib.sha256(protocol_raw).hexdigest(),
    "prior_inventory_sha256": hashlib.sha256(prior_raw).hexdigest(),
    "scope": "Six original endpoint controls at one preselected seed; full trajectories, all original failure prefixes and previous baseline hashes verified. Does not establish all-seed equivalence or historical plotting conventions. Shared-input inventory requires explicit reconciliation; no completed-paper credit.",
}
output.write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps(report, indent=2))
