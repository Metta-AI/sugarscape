"""Reaudit raw segments and reconcile disjoint coverage of one frozen phase grid."""

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("phase", type=int, choices=[1, 2, 3])
parser.add_argument("output", type=Path)
parser.add_argument(
    "--segment",
    nargs=3,
    action="append",
    required=True,
    metavar=("RUN", "START", "RECORDED_ROOT"),
)
parser.add_argument("--require-complete", action="store_true")
args = parser.parse_args()
required = {1: 300, 2: 600, 3: 1200}[args.phase]
auditor = Path(__file__).with_name(
    {1: "audit_phase1.py", 2: "audit_phase2.py", 3: "audit_phase3_movement.py"}[
        args.phase
    ]
)
assert not args.output.exists()
segments = []
occupied = set()
manifests = set()
for run_name, start_text, recorded_root in args.segment:
    run = Path(run_name).resolve()
    start = int(start_text)
    ledger = (run / "completed.jsonl").read_bytes()
    records = [json.loads(line) for line in ledger.splitlines()]
    stop = start + len(records)
    assert 0 <= start < stop <= required
    ordinals = set(range(start, stop))
    assert not occupied.intersection(ordinals), (
        "Overlapping segments or pilot duplicates"
    )
    occupied.update(ordinals)
    manifests.add(hashlib.sha256((run / "manifest.json").read_bytes()).hexdigest())
    segments.append(
        (run, start, stop, recorded_root, hashlib.sha256(ledger).hexdigest())
    )
assert len(manifests) == 1, "Segments must share the identical frozen manifest"
missing = sorted(set(range(required)) - occupied)
if args.require_complete:
    assert not missing, (
        f"Full phase requires {required} conditions; missing {len(missing)}"
    )

args.output.mkdir(parents=True)
reports = []
runs = []
for index, (run, start, stop, recorded_root, ledger_hash) in enumerate(
    sorted(segments, key=lambda s: s[1])
):
    target = args.output.resolve() / f"segment-{index:02d}"
    command = [
        sys.executable,
        str(auditor),
        str(run),
        "prefix",
        str(target),
        "--start-index",
        str(start),
        "--recorded-root",
        recorded_root,
    ]
    subprocess.run(command, check=True)
    report = json.loads((target / "audit.json").read_text())
    assert report["ordinal_interval"] == [start, stop]
    assert report["ledger_sha256"] == ledger_hash, (
        "Ledger changed during reconciliation"
    )
    assert report["manifest_sha256"] in manifests
    assert report["validated_runs"] == stop - start == len(report["runs"])
    assert report["price_step_records"] == 1000 * (stop - start)
    reports.append(
        {
            "run": str(run),
            "recorded_root": recorded_root,
            "ordinal_interval": [start, stop],
            "ledger_sha256": ledger_hash,
            "audit_sha256": hashlib.sha256(
                (target / "audit.json").read_bytes()
            ).hexdigest(),
            "health_records": report["health_records"],
            "price_step_records": report["price_step_records"],
        }
    )
    runs.extend(
        {"ordinal": start + offset, **result}
        for offset, result in enumerate(report["runs"])
    )

result = {
    "phase": args.phase,
    "required_runs": required,
    "validated_runs": len(occupied),
    "complete_grid": not missing,
    "missing_ordinals": missing,
    "health_records": sum(r["health_records"] for r in reports),
    "price_step_records": sum(r["price_step_records"] for r in reports),
    "manifest_sha256": next(iter(manifests)),
    "auditor_sha256": hashlib.sha256(auditor.read_bytes()).hexdigest(),
    "reconciler_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    "segments": reports,
    "runs": runs,
    "scope": "Fresh raw-output audits and disjoint frozen-grid coverage only; no aggregate paper verdict.",
}
(args.output / "reconciliation.json").write_text(
    json.dumps(result, indent=2, allow_nan=False) + "\n"
)
print(
    f"Reconciled {len(occupied)}/{required} disjoint conditions in phase {args.phase}"
)
