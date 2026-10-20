"""Recheck complete native coverage and all Figure 11 comparisons from raw inputs."""

import argparse
import csv
import hashlib
import json
from pathlib import Path
import subprocess
import sys

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("native", type=Path)
parser.add_argument("author", type=Path)
parser.add_argument("output", type=Path)
args = parser.parse_args()
study = Path(__file__).resolve().parents[2]
args.output.mkdir()
assert (
    subprocess.check_output(
        ["git", "-C", str(args.author), "rev-parse", "HEAD"], text=True
    ).strip()
    == "290702073492677f2fc9164419e9d5900d119e02"
)
subprocess.run(
    ["git", "-C", str(args.author), "diff", "--quiet", "HEAD", "--"], check=True
)
author_data = args.author / "sample/data/v100-515.65.01/2.0.0-rc-v100-11.0-beltsoff"
commands = [
    [
        str(study / "audit_native.py"),
        str(args.native),
        str(args.output / "native-audit"),
    ],
    [
        str(study / "plot_native_results.py"),
        str(args.native / "run"),
        str(author_data),
        str(args.output / "figures"),
    ],
    [
        str(study / "compare_native_images.py"),
        str(study / "results/native-image-comparison-2026-10-18/snapshots.json.gz"),
        str(args.author / "sample/figures/visualisation"),
        str(args.output / "images"),
    ],
]
receipts = []
for command in commands:
    result = subprocess.run(
        [sys.executable, *command], capture_output=True, text=True, timeout=180
    )
    receipts.append(
        {
            "command": [sys.executable, *command],
            "exit_code": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
        }
    )
    (args.output / "commands.json").write_text(json.dumps(receipts, indent=2) + "\n")
    assert result.returncode == 0, result.stderr
report = {}
for fresh, previous in [
    ("native-audit/audit.json", "full-native-complete-2026-10-18/audit.json"),
    ("figures/audit.json", "native-figures-2026-10-18/audit.json"),
    ("images/audit.json", "native-image-comparison-2026-10-18/audit.json"),
]:
    raw = (args.output / fresh).read_bytes()
    assert json.loads(raw) == json.loads((study / "results" / previous).read_bytes())
    report[fresh] = {
        "all_fields_match": True,
        "sha256": hashlib.sha256(raw).hexdigest(),
    }
native = json.loads((args.output / "native-audit/audit.json").read_bytes())
assert native["execution_exit_code"] == 0 and native["complete_grid"]
assert native["completed_conditions"] == 84 and native["step_rows"] == 6600
assert native["resolution_rows"] == 162
for name, expected in [
    ("performance_scalingperStep.csv", 4800),
    ("occupationperStep.csv", 1800),
    ("resolution_steps.csv", 162),
]:
    left, right = args.native / "run" / name, author_data / name
    with left.open() as f:
        actual = list(csv.DictReader(f))
    with right.open() as f:
        target = list(csv.DictReader(f))
    assert len(actual) == len(target) == expected
    for a, b in zip(actual, target, strict=True):
        assert {k: v for k, v in a.items() if k != "s_step"} == {
            k: v for k, v in b.items() if k != "s_step"
        }
    report[name] = {
        "exact_non_timing_rows": expected,
        "native_sha256": hashlib.sha256(left.read_bytes()).hexdigest(),
        "author_sha256": hashlib.sha256(right.read_bytes()).hexdigest(),
    }
(args.output / "verification.json").write_text(json.dumps(report, indent=2) + "\n")
