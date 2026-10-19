"""Reconcile the complete deposited filename sets with the exported worklist."""

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
with gzip.open(root / "remaining.csv.gz", "rt", newline="") as stream:
    rows = list(csv.DictReader(stream))
keys = {(row["experiment"], row["entry"]) for row in rows}
assert len(keys) == len(rows) == 99994
excluded = {(row["experiment"], row["entry"]) for row in report["excluded_controls"]}
assert not keys & excluded
expected = set()
for experiment in ["selfishness", "heterogeneous"]:
    path = args.archives / f"blueprints-{experiment}.zip"
    assert (
        hashlib.sha256(path.read_bytes()).hexdigest()
        == report["archive_sha256"][experiment]
    )
    with zipfile.ZipFile(path) as archive:
        expected.update((experiment, name) for name in archive.namelist())
assert expected == keys | excluded
assert (
    hashlib.sha256((root / "remaining.csv.gz").read_bytes()).hexdigest()
    == report["remaining_csv_gz_sha256"]
)
counts = Counter(row["experiment"] for row in rows)
assert counts == {"selfishness": 50497, "heterogeneous": 49497}
result = {
    "remaining_rows": len(rows),
    "unique_remaining_identities": len(keys),
    "excluded_controls": len(excluded),
    "exact_archive_union": True,
    "remaining_by_experiment": dict(counts),
    "scope": "Independent CSV readback and original ZIP filename-set reconciliation. Every original entry occurs exactly once in the remaining worklist or the audited exclusions. This is scheduling evidence, not new simulation output.",
}
assert result == json.loads((root / "readback.json").read_text())
print(json.dumps(result))
