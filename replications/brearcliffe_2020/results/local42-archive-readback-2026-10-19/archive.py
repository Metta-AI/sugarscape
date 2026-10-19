import hashlib
import json
from pathlib import Path
import shutil
import tarfile

root = Path(__file__).resolve().parent
audit_path = root.parent / 'brearcliffe-local-terminal-audit-001/audit.json'
audit = json.loads(audit_path.read_text())
rows = [r for r in audit['completed'] if r['run_id'].startswith('released-code-pair-00-')]
assert sorted(int(r['run_id'].split('-')[-1]) for r in rows) == list(range(42))
assert shutil.disk_usage(root).free > 512 * 1024**2
pins = {}
archive = root / 'local42.tar.gz'
with tarfile.open(archive, 'x:gz') as bundle:
    for row in rows:
        source = Path(row['directory'])
        assert hashlib.sha256((source / 'trajectory.csv').read_bytes()).hexdigest() == row['trajectory_sha256']
        for path in sorted(source.rglob('*')):
            assert not path.is_symlink()
            if path.is_file():
                name = row['run_id'] + '/' + str(path.relative_to(source))
                data = path.read_bytes()
                pins[name] = {'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()}
                bundle.add(path, arcname=name, recursive=False)
readback = {}
with tarfile.open(archive, 'r:gz') as bundle:
    for member in bundle:
        assert member.isfile() and member.name not in readback
        data = bundle.extractfile(member).read()
        readback[member.name] = {'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()}
assert readback == pins
report = {'runs': 42, 'observations': 42 * 20001, 'members': len(pins),
          'archive_bytes': archive.stat().st_size,
          'archive_sha256': hashlib.sha256(archive.read_bytes()).hexdigest(),
          'audit_sha256': hashlib.sha256(audit_path.read_bytes()).hexdigest(),
          'readback': 'Every regular archive member streamed and compared with original byte count and SHA256; no filesystem extraction.',
          'scope': 'Preservation/readback only; full trajectory validity is established by the referenced audit. No new completed inputs or paper verdict.',
          'files': pins}
(root / 'readback.json').write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps({k:v for k,v in report.items() if k != 'files'}))
