"""Reconcile completed recovery after the independently audited paper cohort."""

from pathlib import Path
import json
import subprocess
import os
import sys
import time

root = Path(__file__).resolve().parent
repo = root.parent.parent / "sugarscape-brearcliffe/replications/brearcliffe_2020"
prepared = root.parent / "brearcliffe-ensemble-preparation-001"
dependency = root.parent / "brearcliffe-paper-ec-q-snapshot-001/analysis-terminal.json"
deadline = time.monotonic() + 600
while not dependency.exists():
    assert time.monotonic() < deadline, (
        "Prior cohort audit not yet complete; retain recovery without union credit"
    )
    time.sleep(10)
assert json.loads(dependency.read_text())["exit_code"] == 0
for label, command in [
    ("reconciliation", [sys.executable, str(root / "reconcile.py")]),
    (
        "cohort",
        [
            sys.executable,
            str(repo / "summarize_cohort.py"),
            str(prepared),
            str(root / "union-audit/audit.json"),
            str(root / "cohort"),
            "--interpretation",
            "released-code",
            "--pair-index",
            "15",
        ],
    ),
    (
        "r-validation",
        [
            "/opt/homebrew/bin/Rscript",
            "--vanilla",
            str(repo / "verify_cohort.R"),
            str(prepared),
            str(root / "union-audit/audit.json"),
            str(root / "cohort"),
            str(root / "r-validation.json"),
        ],
    ),
    (
        "comparison",
        [
            sys.executable,
            str(repo / "compare_curves.py"),
            str(root / "cohort"),
            str(
                repo
                / "results/horizontal-calibration-correction-2026-10-19/metric-curves.json.gz"
            ),
            str(root / "comparison"),
        ],
    ),
]:
    with (root / (label + ".log")).open("x") as stream:
        subprocess.run(
            command,
            stdout=stream,
            stderr=subprocess.STDOUT,
            check=True,
            timeout=300,
            env=dict(
                os.environ,
                R_LIBS_USER="/Users/relh/Code/workspace/sugarscape-replication-tools/R-library",
            ),
        )
(root / "analysis-terminal.json").write_text(
    json.dumps(
        {
            "exit_code": 0,
            "completed_inputs": 1152,
            "released_inputs": 800,
            "paper_inputs": 352,
            "observations": 23041152,
            "scope": "Complete released-code ensemble and seven paper cohorts; all paper-table conditions and whole-study synthesis remain.",
        },
        indent=2,
    )
    + "\n"
)
print(
    "Recovery reconciliation, complete SARSA/SARSA cohort, R check and comparison passed",
    flush=True,
)
