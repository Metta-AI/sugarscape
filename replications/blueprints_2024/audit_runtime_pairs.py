"""Audit the two recovered supplementary CPython/PyPy control pairs."""

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("run", type=Path)
parser.add_argument("archive", type=Path)
parser.add_argument("output", type=Path)
args = parser.parse_args()
args.output.mkdir(parents=True, exist_ok=False)
manifest = json.loads((args.run / "manifest.json").read_text())
pins = json.loads(Path(__file__).with_name("source-sha256.json").read_text())
assert manifest["source_sha256"] == pins["source_sha256"]
assert manifest["cpython_version"].strip() == "Python 3.11.14"
assert "Python 3.11.13" in manifest["pypy_version"]
assert "PyPy 7.3.20" in manifest["pypy_version"]
assert manifest["entries"] == [
    f"{factor}-benthamHalfLookaheadBinary175856849482260318.config"
    for factor in ["0.37", "0.73"]
]
complete = json.loads((args.run / "complete.json").read_text())
ledger = [
    json.loads(line) for line in (args.run / "completed.jsonl").read_text().splitlines()
]
assert ledger == complete["receipts"] and len(ledger) == 4
assert {(r["flavor"], r["entry"]) for r in ledger} == {
    (flavor, entry) for flavor in ["cpython", "pypy"] for entry in manifest["entries"]
}
reports = []
for entry in manifest["entries"]:
    stem = entry.removesuffix(".config")
    reference = args.run / ("cpython-" + stem)
    alternate = args.run / ("pypy-" + stem)
    subprocess.run(
        [
            sys.executable,
            str(Path(__file__).with_name("audit_supplement.py")),
            str(args.archive),
            str(reference),
            str(args.output / stem),
        ],
        check=True,
    )
    left = json.loads((reference / "config.json").read_text())
    right = json.loads((alternate / "config.json").read_text())
    assert right == left | {"logfile": right["logfile"]}
    assert (reference / "original.config").read_bytes() == (
        alternate / "original.config"
    ).read_bytes()
    expected = (reference / "trajectory.json").read_bytes()
    actual = (alternate / "trajectory.json").read_bytes()
    assert expected == actual
    rows = json.loads(actual)
    assert len(rows) == 5001
    checksum = hashlib.sha256(actual).hexdigest()
    timings = {}
    for flavor in ["cpython", "pypy"]:
        receipt = next(
            r for r in ledger if r["flavor"] == flavor and r["entry"] == entry
        )
        terminal = json.loads((args.run / f"{flavor}-{stem}.exit.json").read_text())
        assert receipt == terminal | {"trajectory_sha256": checksum}
        assert receipt["exit_code"] == 0
        timings[flavor] = receipt["elapsed_seconds"]
    recorded = next(r for r in complete["comparisons"] if r["entry"] == entry)
    assert recorded == {
        "entry": entry,
        "byte_exact": True,
        "records_exact": True,
        "cpython_observations": 5001,
        "pypy_observations": 5001,
        "first_different_record": None,
        "cpython_sha256": checksum,
        "pypy_sha256": checksum,
        "cpython_final_population": rows[-1]["population"],
        "pypy_final_population": rows[-1]["population"],
    }
    reports.append(
        {
            "entry": entry,
            "observations": len(rows),
            "sha256": checksum,
            "final_population": rows[-1]["population"],
            "elapsed_seconds": timings,
        }
    )
report = {
    "paired_conditions": 2,
    "native_runs": 4,
    "paired_observations": 10002,
    "byte_exact_pairs": 2,
    "runs": reports,
    "scope": "Two additional original-input runtime controls, not universal runtime equivalence. "
    "Concurrent shared-host timings are descriptive, not a controlled speedup estimate. "
    "No full supplementary sweep or paper completion.",
}
(args.output / "audit.json").write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps(report))
