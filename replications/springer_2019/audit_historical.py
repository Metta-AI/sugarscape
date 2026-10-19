"""Audit original-source compiler qualification archives without treating timeouts as results."""

import argparse
import hashlib
import io
import json
from pathlib import Path
import tarfile
import zipfile

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("archive", type=Path)
parser.add_argument("receipt", type=Path)
parser.add_argument("output", type=Path)
args = parser.parse_args()
receipt = json.loads(args.receipt.read_text())["receipt"]
assert args.archive.stat().st_size == receipt["bytes"]
assert hashlib.sha256(args.archive.read_bytes()).hexdigest() == receipt["sha256"]
with tarfile.open(args.archive) as archive:
    files = {
        m.name: archive.extractfile(m).read()
        for m in archive.getmembers()
        if m.isfile()
    }
prefix = "diagnostic/native/"
raw = files[prefix + "artifact.zip"]
assert (
    hashlib.sha256(raw).hexdigest()
    == "75421734305809c5999904082616996a904a19a5e43466cf076ec10660e559a1"
)
with zipfile.ZipFile(io.BytesIO(raw)) as archive:
    source_hashes = {
        m.filename: hashlib.sha256(archive.read(m)).hexdigest()
        for m in archive.infolist()
        if not m.is_dir()
    }
for name, digest in source_hashes.items():
    assert hashlib.sha256(files[prefix + "source/" + name]).hexdigest() == digest
assert json.loads(files[prefix + "source-sha256.json"]) == source_hashes
records = json.loads(files[prefix + "records.json"])
builds = {}
executions = []
for row in records:
    key = (row["mode"], row["grid_side"])
    if row["kind"] == "build":
        assert key not in builds
        builds[key] = row
        assert "-Ilib/cub" in row["command"]
        assert "arch=compute_61,code=compute_61" in row["command"]
        assert not any(x.startswith("-DPARAM_MAX_OBJ") for x in row["command"])
    else:
        assert row["kind"] == "execution" and builds[key]["returncode"] == 0
        assert (
            hashlib.sha256(files[prefix + f"{key[0]}-{key[1]}"]).hexdigest()
            == row["binary_sha256"]
        )
        executions.append(row)
assert "V9.1.85" in files[prefix + "compiler.txt"].decode()
assert "5.4.0-6ubuntu1~16.04.12" in files[prefix + "host-compiler.txt"].decode()
report = {
    "archive_sha256": receipt["sha256"],
    "unchanged_source_files": len(source_hashes),
    "builds": list(builds.values()),
    "executions": executions,
    "completed_executions": sum(x["returncode"] == 0 for x in executions),
    "terminal": json.loads(files["diagnostic/terminal.json"]),
    "scope": "Original source and binary integrity plus execution outcomes. No phase localization without progress instrumentation, no full-state validation or benchmark comparison.",
}
args.output.mkdir(parents=True, exist_ok=False)
(args.output / "audit.json").write_text(json.dumps(report, indent=2) + "\n")
for name, data in files.items():
    if (
        name
        in [
            "diagnostic/native.log",
            "diagnostic/terminal.json",
            "diagnostic/qualify_historical.py",
            "diagnostic/loader-cache.txt",
            "diagnostic/nvvm-sha256.txt",
        ]
        or name.startswith(prefix)
        and (
            name.endswith((".log", ".txt"))
            or name in [prefix + "records.json", prefix + "source-sha256.json"]
        )
    ):
        (args.output / Path(name).name).write_bytes(data)
