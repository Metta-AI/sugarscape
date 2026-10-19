from pathlib import Path
import hashlib
import json
import shutil
import subprocess
import sys
import tarfile

root = Path(__file__).resolve().parent
assert json.loads((root / 'attempt-001/complete.json').read_text())['exit_code'] == 0
subprocess.run([sys.executable, str(root / 'audit-complete.py'), str(root), str(root / 'audit.json')], check=True, timeout=60)
files = sorted(p for p in root.rglob('*') if p.is_file())
manifest = {str(p.relative_to(root)): {'bytes': p.stat().st_size, 'sha256': hashlib.sha256(p.read_bytes()).hexdigest()} for p in files}
archive = root / 'native-strata.tar.gz'
assert not archive.exists()
with tarfile.open(archive, 'w:gz') as bundle:
    for path in files:
        bundle.add(path, arcname=str(path.relative_to(root)), recursive=False)
readback = root / 'readback'
readback.mkdir()
with tarfile.open(archive) as bundle:
    for member in bundle:
        assert member.isfile() and not Path(member.name).is_absolute() and '..' not in Path(member.name).parts
    bundle.extractall(readback, filter='data')
actual = {str(p.relative_to(readback)): {'bytes': p.stat().st_size, 'sha256': hashlib.sha256(p.read_bytes()).hexdigest()} for p in readback.rglob('*') if p.is_file()}
assert actual == manifest
subprocess.run([sys.executable, str(readback / 'audit-complete.py'), str(readback), str(root / 'repeat-audit.json')], check=True, timeout=60)
assert (root / 'audit.json').read_bytes() == (root / 'repeat-audit.json').read_bytes()
(root / 'archive-readback.json').write_text(json.dumps({'archive_bytes': archive.stat().st_size, 'archive_sha256': hashlib.sha256(archive.read_bytes()).hexdigest(), 'members': manifest, 'all_members_exact': True, 'fresh_extraction_audit_byte_identical': True}, indent=2) + '\n')
assert archive.stat().st_size < 45 * 1024**2
repo = Path('/Users/relh/Code/workspace/sugarscape-raimbault/replications/raimbault_2019')
result = repo / 'results/vision-cache-strata-complete-2026-10-19'
result.mkdir()
for name in ['native-strata.tar.gz', 'archive-readback.json', 'audit.json', 'audit-complete.py', 'protocol.json', 'preserve.py']:
    shutil.copyfile(root / name, result / name)
print('Archive and full audit verified and copied for publication', flush=True)
