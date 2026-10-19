"""Compare full fresh-worker output with the retained qualified archive."""

from pathlib import Path
import csv
import hashlib
import json
import math
import tarfile

root = Path(__file__).resolve().parent
archive = root / "qualification-results.tar.gz"
prior = (
    root.parent
    / "brearcliffe-existing-host-qualification-001/qualification-results.tar.gz"
)
assert (
    hashlib.sha256(archive.read_bytes()).hexdigest()
    == "877a11a88c819a9d825fcde1e784985e72e2385dc8a7f098182fc60075d47ed3"
)
assert (
    hashlib.sha256(prior.read_bytes()).hexdigest()
    == "197222dc91da2fdbb7377e989e828ac3e194e11091527df1f500ebbe25e2a7df"
)
reports = []
with tarfile.open(archive) as current, tarfile.open(prior) as reference:
    members = current.getmembers()
    assert len({m.name for m in members}) == len(members)
    assert all(m.isfile() or m.isdir() for m in members)
    hashes = {
        m.name: hashlib.sha256(current.extractfile(m).read()).hexdigest()
        for m in members
        if m.isfile()
    }
    for name in [
        "payload/cases.json",
        "payload/payload-sha256.json",
        "payload/plan.json",
    ]:
        assert current.extractfile(name).read() == reference.extractfile(name).read()
    cases = json.load(current.extractfile("payload/cases.json"))
    for case in cases:
        directory = "payload/results/" + case["name"] + "/"
        raw = current.extractfile(directory + "trajectory.csv").read()
        old = reference.extractfile(directory + "trajectory.csv").read()
        assert raw == old and hashlib.sha256(raw).hexdigest() == case["sha256"]
        rows = list(csv.DictReader(raw.decode().splitlines()))
        assert len(rows) == 20001
        for tick, row in enumerate(rows):
            assert len(row) == 17 and float(row["tick"]) == tick
            assert all(math.isfinite(float(v)) for v in row.values())
        terminal = json.load(current.extractfile(directory + "terminal.json"))
        assert terminal["exit_code"] == 0 and 0 < terminal["elapsed_seconds"] < 1800
        reports.append(
            {
                "case": case["name"],
                "observations": 20001,
                "numeric_fields": 320016,
                "bytes_exact": True,
                "trajectory_sha256": case["sha256"],
                "elapsed_seconds": terminal["elapsed_seconds"],
            }
        )
    summary = json.load(current.extractfile("payload/results/summary.json"))
    assert summary["exit_code"] == 0 and len(summary["cases"]) == 2
report = {
    "archive_sha256": hashlib.sha256(archive.read_bytes()).hexdigest(),
    "archive_bytes": archive.stat().st_size,
    "prior_archive_sha256": hashlib.sha256(prior.read_bytes()).hexdigest(),
    "member_sha256": hashes,
    "cases": reports,
    "compared_numeric_fields": 640032,
    "conservative797_all_slow_case_hours": 797
    * max(x["elapsed_seconds"] for x in reports)
    / 8
    / 3600,
    "scope": "Both full cross-host trajectories equal the previously qualified archive byte-for-byte. Runtime qualification, not new ensemble completion credit.",
}
(root / "audit.json").write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps({k: v for k, v in report.items() if k != "member_sha256"}))
