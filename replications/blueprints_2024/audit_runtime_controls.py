"""Independently compare all six completed runtime controls to retained CPython bytes."""

import argparse
import hashlib
import json
from pathlib import Path

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("pypy", type=Path)
parser.add_argument("reference", type=Path)
parser.add_argument("output", type=Path)
a = parser.parse_args()
manifest = json.loads((a.pypy / "manifest.json").read_text())
complete = json.loads((a.pypy / "complete.json").read_text())
assert "3.11.13" in manifest["version"] and "7.3.20" in manifest["version"]
assert (
    manifest["runtime_sha256"]
    == "1410db3a7ae47603e2b7cbfd7ff6390b891b2e041c9eb4f1599f333677bccb3e"
)
assert len(manifest["conditions"]) == complete["completed_controls"] == 6
assert len({entry for kind, entry in manifest["conditions"]}) == 6
ledger = [
    json.loads(line) for line in (a.pypy / "completed.jsonl").read_text().splitlines()
]
assert len(ledger) == 6 and sorted(ledger, key=lambda r: r["entry"]) == sorted(
    complete["runs"], key=lambda r: r["entry"]
)
reports = []
for kind, entry in manifest["conditions"]:
    name = entry.removesuffix(".config")
    current = a.pypy / name
    prior = a.reference / "runs" / name
    expected_manifest = json.loads((prior / "manifest.json").read_text())
    assert expected_manifest["python"].startswith("3.11.14")
    assert expected_manifest["release"] == "b9ca671ab7591c7b3606f2d76c33eda344d626d1"
    assert expected_manifest["source_sha256"] == manifest["source_sha256"]
    expected_config = json.loads((prior / "config.json").read_text())
    actual_config = json.loads((current / "config.json").read_text())
    assert actual_config == expected_config | {"logfile": actual_config["logfile"]}
    assert json.loads((current / "exit.json").read_text())["exit_code"] == 0
    expected = (prior / "trajectory.json").read_bytes()
    actual = (current / "trajectory.json").read_bytes()
    expected_result = json.loads((prior / "result.json").read_text())
    result = json.loads((current / "result.json").read_text())
    assert result == next(r for r in ledger if r["entry"] == entry)
    assert (
        hashlib.sha256(expected).hexdigest()
        == expected_result["trajectory_sha256"]
        == result["reference_sha256"]
    )
    assert hashlib.sha256(actual).hexdigest() == result["trajectory_sha256"]
    left, right = json.loads(expected), json.loads(actual)
    assert len(left) == len(right) == 5001
    assert [r["timestep"] for r in right] == list(range(5001))
    assert result["byte_exact"] == (expected == actual)
    assert result["records_exact"] == (left == right)
    assert result["experiment"] == kind
    reports.append(
        {
            "entry": entry,
            "byte_exact": expected == actual,
            "records_exact": left == right,
            "observations": len(right),
            "sha256": hashlib.sha256(actual).hexdigest(),
            "elapsed_seconds": result["elapsed_seconds"],
            "reference_elapsed_seconds": expected_result["elapsed_seconds"],
        }
    )
assert sum(r["byte_exact"] for r in reports) == complete["byte_exact_trajectories"]
assert sum(r["records_exact"] for r in reports) == complete["exact_trajectories"]
report = {
    "controls": 6,
    "observations": sum(r["observations"] for r in reports),
    "byte_exact": sum(r["byte_exact"] for r in reports),
    "runs": reports,
    "scope": "Independent full-byte comparison to previously audited retained CPython trajectories; shared-host timings do not establish controlled speedup. One seed and six configurations do not establish universal runtime equivalence or paper completion.",
}
with a.output.open("x") as stream:
    stream.write(json.dumps(report, indent=2) + "\n")
print(json.dumps({k: v for k, v in report.items() if k != "runs"}))
