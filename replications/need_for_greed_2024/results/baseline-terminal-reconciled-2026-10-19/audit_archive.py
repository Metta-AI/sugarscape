"""Independently reopen sealed recovery trajectories against frozen original evidence."""

from pathlib import Path
import hashlib
import json
import math
import sys
import tarfile
import zipfile

base, archive, output = map(Path, sys.argv[1:])
assert not output.exists()
payload = base / "need-for-greed-baseline-recovery-001/payload"
plan_raw = (payload / "plan.json").read_bytes()
plan = {r["entry"]: r for r in json.loads(plan_raw)["rows"]}
assert len(plan) == 333
prior = json.loads(
    (base / "need-for-greed-retained-audit-reuse-001/inventory.json").read_bytes()
)
previous = {r["entry"]: r for r in prior["runs"]}
pins = json.loads((payload / "source-sha256.json").read_bytes())
source_zip = base / "papers/need-for-greed.zip"
assert (
    hashlib.sha256(source_zip.read_bytes()).hexdigest()
    == "e41c89ed31811b2d100c0a54f9c0110f0572a980b599e2417b2653b934fbe440"
)
reports = []
failures = []
member_hashes = {}
with tarfile.open(archive) as tar, zipfile.ZipFile(source_zip) as original:
    members = tar.getmembers()
    assert len({m.name for m in members}) == len(members)
    assert all(m.isfile() or m.isdir() for m in members)
    assert all(
        not Path(m.name).is_absolute() and ".." not in Path(m.name).parts
        for m in members
    )
    for m in members:
        if m.isfile():
            member_hashes[m.name] = hashlib.sha256(
                tar.extractfile(m).read()
            ).hexdigest()
    for name in (
        "plan.json",
        "run_native.py",
        "source-sha256.json",
        "run_recovery.py",
        "bootstrap.sh",
    ):
        assert tar.extractfile(name).read() == (payload / name).read_bytes()
    receipts = sorted(m.name for m in members if m.name.endswith(".receipt.json"))
    assert receipts
    for name in receipts:
        receipt = json.load(tar.extractfile(name))
        entry = receipt["entry"]
        assert entry in plan and receipt["exit_code"] in (0, 124)
        frozen = plan[entry]
        directory = "runs/" + entry.removesuffix(".config") + "/"
        config_bytes = tar.extractfile(directory + "original.config").read()
        assert config_bytes == original.read(entry)
        assert (
            hashlib.sha256(config_bytes).hexdigest() == frozen["configuration_sha256"]
        )
        config = json.loads(config_bytes)
        effective = json.load(tar.extractfile(directory + "config.json"))
        assert effective == config | {"logfile": effective["logfile"]}
        assert (
            effective["logfile"]
            == "/root/sugarscape/need-for-greed-baseline-recovery-001/"
            + directory
            + "trajectory.json"
        )
        manifest = json.load(tar.extractfile(directory + "manifest.json"))
        assert manifest["source_sha256"] == pins["source_sha256"]
        assert manifest["release"] == pins["release"]
        assert (
            manifest["entry"] == entry
            and manifest["seed"] == frozen["seed"] == config["seed"]
        )
        assert (
            manifest["effective_model"]
            == frozen["model"]
            == config["agentDecisionModels"][0]
        )
        assert manifest["pythonhashseed"] == "0" and manifest[
            "python_version"
        ].startswith("3.11.14")
        terminal = json.load(tar.extractfile(directory + "terminal.json"))
        assert terminal["exit_code"] == receipt["exit_code"]
        if terminal["exit_code"] == 124:
            assert receipt["verified"] is False
            assert entry == "egoisticHalfLookaheadBinary530238075247992587.config"
            assert directory + "result.json" not in member_hashes
            partial = tar.extractfile(directory + "trajectory.json").read()
            retained = (
                base
                / "need-for-greed-baseline-runtime-review-001/failed-trajectory.json"
            ).read_bytes()
            assert partial == retained
            failures.append(
                {
                    "entry": entry,
                    "exit_code": 124,
                    "bytes": len(partial),
                    "sha256": hashlib.sha256(partial).hexdigest(),
                    "retained_failed_prefix_exact": True,
                }
            )
            continue
        assert receipt["verified"] is True
        raw = tar.extractfile(directory + "trajectory.json").read()
        digest = hashlib.sha256(raw).hexdigest()
        assert (
            digest
            == frozen["trajectory_sha256"]
            == previous[entry]["result"]["trajectory_sha256"]
        )
        rows = json.loads(raw)
        assert (
            len(rows)
            == frozen["observations"]
            == previous[entry]["result"]["observations"]
        )
        assert rows[0]["population"] == 250
        arrays = {"agentWealths", "agentTimesToLive", "agentTimesToLiveAgeLimited"}
        fields = set(rows[0])
        for t, row in enumerate(rows):
            assert (
                set(row) == fields
                and row["timestep"] == t
                and row["seed"] == frozen["seed"]
            )
            assert (
                0 <= row["population"] <= 2500
                and int(row["population"]) == row["population"]
            )
            assert {k for k, v in row.items() if isinstance(v, list)} == arrays
            assert all(math.isfinite(v) for k, v in row.items() if k not in arrays)
            assert all(math.isfinite(v) for k in arrays for v in row[k])
        assert rows[-1]["timestep"] == 5000 or rows[-1]["population"] == 0
        assert (
            rows[-1]["population"]
            == frozen["final_population"]
            == previous[entry]["result"]["final_population"]
        )
        reports.append(
            {
                "entry": entry,
                "observations": len(rows),
                "trajectory_sha256": digest,
                "final_population": rows[-1]["population"],
            }
        )
    assert len({r["entry"] for r in reports}) == len(reports)
    assert {m.name.split("/")[1] for m in members if m.name.startswith("runs/")} == {
        r["entry"].removesuffix(".config") for r in reports + failures
    }
report = {
    "archive_sha256": hashlib.sha256(archive.read_bytes()).hexdigest(),
    "plan_sha256": hashlib.sha256(plan_raw).hexdigest(),
    "runs": reports,
    "failures": failures,
    "inputs": len(reports),
    "observations": sum(r["observations"] for r in reports),
    "member_sha256": member_hashes,
    "scope": "Independent raw recovery audit; no shared coverage reconciliation or completed-paper credit.",
}
output.write_text(json.dumps(report, indent=2) + "\n")
print(
    json.dumps({k: v for k, v in report.items() if k not in ("runs", "member_sha256")})
)
