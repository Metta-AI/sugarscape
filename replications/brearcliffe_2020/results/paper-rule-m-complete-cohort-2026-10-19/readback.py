from pathlib import Path
import hashlib
import json
import shutil
import subprocess
import sys
import tarfile

root = Path(__file__).resolve().parent
report = json.loads((root / 'snapshot.json').read_text())
archive = root / 'paper-pair00-49.tar.gz'
assert archive.stat().st_size == report['archive_bytes']
assert hashlib.sha256(archive.read_bytes()).hexdigest() == report['archive_sha256']
assert shutil.disk_usage(root).free > 512 * 1024**2
extracted = root / 'readback'
extracted.mkdir()
with tarfile.open(archive) as bundle:
    for member in bundle:
        assert not Path(member.name).is_absolute() and '..' not in Path(member.name).parts
        assert member.isfile() or member.isdir()
    bundle.extractall(extracted, filter='data')
actual = {}
for p in sorted((extracted / 'runs').rglob('*')):
    if p.is_file():
        b = p.read_bytes()
        actual[str(p.relative_to(extracted))] = {'bytes': len(b), 'sha256': hashlib.sha256(b).hexdigest()}
assert actual == report['files']
old = json.loads((root.parent / 'brearcliffe-q-sarsa-snapshot-001/union-audit/audit.json').read_text())
runs = [r['directory'] for r in old['completed']] + [str(p) for p in sorted((extracted / 'runs').iterdir())]
repo = Path('/Users/relh/Code/workspace/sugarscape-brearcliffe/replications/brearcliffe_2020')
prepared = root.parent / 'brearcliffe-ensemble-preparation-001'
subprocess.run([sys.executable, str(repo / 'audit_ensemble.py'), str(prepared), str(root / 'union-audit'), *runs], check=True)
new = json.loads((root / 'union-audit/audit.json').read_text())
by_id = {r['run_id']: r for r in new['completed']}
assert len(by_id) == 652 and all(by_id[r['run_id']] == r for r in old['completed'])
(root / 'validation.json').write_text(json.dumps({'archive_members_verified': len(actual), 'new_inputs': 49, 'previous_inputs_preserved_exactly': 603, 'completed_inputs': 652, 'observations': new['observations'], 'pair00_complete': 50, 'scope': 'Full trajectories audited; paper comparison remains separate.'}, indent=2) + '\n')
subprocess.run([sys.executable, str(repo / 'summarize_cohort.py'), str(prepared), str(root / 'union-audit/audit.json'), str(root / 'cohort'), '--interpretation', 'paper-table', '--pair-index', '0'], check=True)
