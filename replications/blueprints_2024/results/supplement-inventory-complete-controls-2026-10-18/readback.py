"""Reconcile corrected remaining work with original archives and prior inventory."""

import argparse
from collections import Counter
import csv
import gzip
import hashlib
import json
from pathlib import Path
import zipfile

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("archives", type=Path)
args = parser.parse_args()
root = Path(__file__).parent
report = json.loads((root / "inventory.json").read_text())
previous = root.parent / "supplement-inventory-2026-10-18"
with gzip.open(root / "remaining.csv.gz", "rt", newline="") as stream:
    rows = list(csv.DictReader(stream))
with gzip.open(previous / "remaining.csv.gz", "rt", newline="") as stream:
    prior_rows = list(csv.DictReader(stream))
current = {(row["experiment"], row["entry"]): row for row in rows}
prior = {(row["experiment"], row["entry"]): row for row in prior_rows}
assert len(current) == len(rows) == 99992
assert len(prior) == len(prior_rows) == 99994
removed = set(prior) - set(current)
assert removed == {
    ("selfishness", "0.37-benthamHalfLookaheadBinary175856849482260318.config"),
    ("selfishness", "0.73-benthamHalfLookaheadBinary175856849482260318.config"),
}
assert all(row == prior[key] for key, row in current.items())
excluded = {(row["experiment"], row["entry"]) for row in report["excluded_controls"]}
assert len(excluded) == 8 and not set(current) & excluded
expected = set()
for experiment in ["selfishness", "heterogeneous"]:
    path = args.archives / f"blueprints-{experiment}.zip"
    assert (
        hashlib.sha256(path.read_bytes()).hexdigest()
        == report["archive_sha256"][experiment]
    )
    with zipfile.ZipFile(path) as archive:
        expected.update((experiment, name) for name in archive.namelist())
assert expected == set(current) | excluded
assert (
    hashlib.sha256((root / "remaining.csv.gz").read_bytes()).hexdigest()
    == report["remaining_csv_gz_sha256"]
)
counts = Counter(row["experiment"] for row in rows)
assert counts == {"selfishness": 50495, "heterogeneous": 49497}
result = {
    "remaining_rows": len(rows),
    "unique_remaining_identities": len(current),
    "excluded_original_inputs": len(excluded),
    "exact_archive_union": True,
    "prior_inventory_rows": len(prior),
    "removed_already_completed_inputs": [
        {"experiment": experiment, "entry": entry}
        for experiment, entry in sorted(removed)
    ],
    "all_other_rows_unchanged": True,
    "remaining_by_experiment": dict(counts),
    "scope": "Complete original ZIP identity coverage, disjoint completed-input exclusions, and exact correction of the two missed paired-control inputs. No simulations dispatched or new completion credit.",
}
assert result == json.loads((root / "readback.json").read_text())
print(json.dumps(result))
