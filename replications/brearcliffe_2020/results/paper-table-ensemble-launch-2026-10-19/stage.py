"""Regenerate and verify the frozen paper-table inputs without running simulations."""

from pathlib import Path
import csv
import hashlib
import json
import subprocess
import sys
import tarfile

root = Path(__file__).resolve().parent
archive = root / "staged-input/paper-input.tar.gz"
assert archive.stat().st_size == 63666
assert (
    hashlib.sha256(archive.read_bytes()).hexdigest()
    == "60b25a1cfc539b85da5ef4a9ba60f593b74bdb2dd8e136905faceb109ee5c1a6"
)
with tarfile.open(archive) as tar:
    assert all(m.isfile() or m.isdir() for m in tar.getmembers())
    tar.extractall(root, filter="data")
payload = root / "payload"
for name, digest in json.loads((payload / "payload-sha256.json").read_bytes()).items():
    assert hashlib.sha256((payload / name).read_bytes()).hexdigest() == digest
subprocess.run(
    [
        sys.executable,
        str(payload / "prepare_ensemble.py"),
        str(payload / "author-model.nlogo"),
        str(root / "prepared"),
    ],
    check=True,
)
manifest = root / "prepared/manifest.csv"
assert (
    hashlib.sha256(manifest.read_bytes()).hexdigest()
    == "3633edf2ca2ec1bd59222e15241655c38c7ec0cacffd1948294ed7c69be85c37"
)
with manifest.open() as f:
    expected = {r["run_id"]: r for r in csv.DictReader(f)}
with (payload / "assignment.csv").open() as f:
    rows = list(csv.DictReader(f))
assert len(rows) == len({r["run_id"] for r in rows}) == 797
assert all(
    r == expected[r["run_id"]] and r["interpretation"] == "paper-table" for r in rows
)
for row in expected.values():
    assert (
        hashlib.sha256((root / "prepared" / row["model"]).read_bytes()).hexdigest()
        == row["model_sha256"]
    )
(root / "staging-validation.json").write_text(
    json.dumps(
        {
            "prepared_models": 1600,
            "assigned_inputs": 797,
            "manifest_sha256": hashlib.sha256(manifest.read_bytes()).hexdigest(),
            "assignment_sha256": hashlib.sha256(
                (payload / "assignment.csv").read_bytes()
            ).hexdigest(),
            "simulations_executed": 0,
        },
        indent=2,
    )
    + "\n"
)
