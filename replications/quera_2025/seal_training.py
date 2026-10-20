"""Seal every audited native training file into bounded, verified archives."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import tarfile

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("native", type=Path)
parser.add_argument("audit", type=Path)
parser.add_argument("native_exit", type=Path)
parser.add_argument("expected_epochs", type=int)
parser.add_argument("output", type=Path)
args = parser.parse_args()
assert 0 < args.expected_epochs <= 5000
assert not args.output.exists()
audit = json.loads(args.audit.read_bytes())
assert audit["epochs"] == args.expected_epochs
assert json.loads(args.native_exit.read_bytes())["exit_code"] == 0
assert audit["parameter_count"] == 19114
assert audit["optimizer_components_verified"] == 19114 * args.expected_epochs
expected = audit["sha256"]
actual_files = {p.name: p for p in args.native.iterdir()}
assert set(actual_files) == set(expected)
assert all(p.is_file() and not p.is_symlink() for p in actual_files.values())
total_bytes = sum(p.stat().st_size for p in actual_files.values())
assert shutil.disk_usage(args.output.parent).free > total_bytes * 2 + 1024**3
for name, digest in expected.items():
    assert hashlib.sha256(actual_files[name].read_bytes()).hexdigest() == digest, name

epoch_names = {
    f"{kind}-{epoch}.csv"
    for epoch in range(1, args.expected_epochs + 1)
    for kind in ["parameters", "gradient", "validation-samples"]
}
assert epoch_names <= set(expected)
metadata = sorted(set(expected) - epoch_names)
assert metadata == sorted([
    "best-parameters.csv", "completion.txt", "epochs.csv",
    "initial-parameters.csv", "observation.csv", "validation.csv",
])
groups = [("metadata", metadata)]
for first in range(1, args.expected_epochs + 1, 500):
    last = min(first + 499, args.expected_epochs)
    names = [
        f"{kind}-{epoch}.csv"
        for epoch in range(first, last + 1)
        for kind in ["parameters", "gradient", "validation-samples"]
    ]
    groups.append((f"epochs-{first:04d}-{last:04d}", names))
assert sum(len(names) for _, names in groups) == len(expected)

args.output.mkdir()
archives = []
seen = set()
for label, names in groups:
    path = args.output / f"{label}.tar.gz"
    with tarfile.open(path, "w:gz", compresslevel=1) as bundle:
        for name in names:
            bundle.add(actual_files[name], arcname=name, recursive=False)
    assert path.stat().st_size <= 256 * 1024**2
    with tarfile.open(path) as bundle:
        members = bundle.getmembers()
        assert len(members) == len(names)
        assert {member.name for member in members} == set(names)
        for member in members:
            assert member.isfile() and member.name not in seen
            assert hashlib.sha256(bundle.extractfile(member).read()).hexdigest() == expected[member.name]
            seen.add(member.name)
    archives.append({
        "name": path.name, "bytes": path.stat().st_size,
        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(), "members": names,
    })
assert seen == set(expected)
manifest = {
    "method": audit["method"], "epochs": args.expected_epochs,
    "native_files": len(expected), "native_bytes": total_bytes,
    "audit_sha256": hashlib.sha256(args.audit.read_bytes()).hexdigest(),
    "native_exit_sha256": hashlib.sha256(args.native_exit.read_bytes()).hexdigest(),
    "member_sha256": expected, "archives": archives,
    "all_archive_members_match_audited_native_files": True,
    "scope": "Local sealed archive verification only; remote upload and fresh readback remain required.",
}
(args.output / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
print(json.dumps({key: manifest[key] for key in [
    "method", "epochs", "native_files", "native_bytes",
    "all_archive_members_match_audited_native_files",
]}))
