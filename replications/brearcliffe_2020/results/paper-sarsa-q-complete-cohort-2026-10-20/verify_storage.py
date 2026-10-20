"""Verify a fresh storage download and every archived file against the sealed snapshot."""
from pathlib import Path
import hashlib
import json
import subprocess
import tarfile

root = Path(__file__).resolve().parent
snapshot = json.loads((root / "snapshot.json").read_bytes())
key = "relh-sugarscape-evidence-20261017/brearcliffe-paper-sarsa-q-sealed-001/paper-pair14-50.tar.gz"
collector = root.parent / "storage-handoff-20261017-001/brearcliffe-paper-sarsa-q-sealed-001"
status = json.loads((collector / "paper-pair14-50.tar.gz.status.json").read_bytes())
assert status["status"] == "complete"
archive = root / "storage-paper-pair14-50.tar.gz"
assert not archive.exists()
process = subprocess.run(["autor", "storage", "cp", key, str(archive), "--json"], capture_output=True, text=True, timeout=180)
(root / "storage-download.json").write_text(json.dumps({"exit_code": process.returncode, "stdout": process.stdout, "stderr": process.stderr}, indent=2) + "\n")
assert process.returncode == 0, process.stderr
assert archive.stat().st_size == snapshot["archive_bytes"]
assert hashlib.sha256(archive.read_bytes()).hexdigest() == snapshot["archive_sha256"]
with tarfile.open(archive) as bundle:
    members = bundle.getmembers()
    assert len({m.name for m in members}) == len(members)
    assert all(m.isfile() or m.isdir() for m in members)
    assert all(not Path(m.name).is_absolute() and ".." not in Path(m.name).parts for m in members)
    hashes = {m.name: {"bytes": m.size, "sha256": hashlib.sha256(bundle.extractfile(m).read()).hexdigest()} for m in members if m.isfile()}
assert {k: v for k, v in hashes.items() if k.startswith("runs/")} == snapshot["files"]
result = {"storage_object": key, "archive_bytes": archive.stat().st_size, "archive_sha256": snapshot["archive_sha256"], "fresh_download_exact": True, "snapshot_run_members_exact": True, "member_sha256": hashes}
(root / "storage-readback.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps({k: v for k, v in result.items() if k != "member_sha256"}))
