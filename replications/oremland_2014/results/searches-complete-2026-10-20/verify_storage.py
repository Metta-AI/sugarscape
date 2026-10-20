"""Verify a fresh archive download against the complete search manifest."""
from pathlib import Path
import hashlib
import json
import sys
import tarfile

archive, audit_path, output = map(Path, sys.argv[1:])
assert not output.exists()
audit = json.loads(audit_path.read_bytes())
assert archive.stat().st_size == audit["archive_bytes"]
assert hashlib.sha256(archive.read_bytes()).hexdigest() == audit["archive_sha256"]
with tarfile.open(archive) as bundle:
    members = bundle.getmembers()
    assert len(members) == len({m.name for m in members}) == audit["archive_members_verified"]
    assert all(m.isfile() and not Path(m.name).is_absolute() and ".." not in Path(m.name).parts for m in members)
    actual = {m.name: hashlib.sha256(bundle.extractfile(m).read()).hexdigest() for m in members}
assert actual == audit["member_sha256"]
output.write_text(json.dumps({"archive_bytes": archive.stat().st_size, "archive_sha256": audit["archive_sha256"], "all_archive_members_exact": True, "archive_members_verified": len(actual)}, indent=2) + "\n")
