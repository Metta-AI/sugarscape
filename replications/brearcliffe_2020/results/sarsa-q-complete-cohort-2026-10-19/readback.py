from pathlib import Path
import hashlib
import json
import shutil
import subprocess
import sys
import tarfile

root = Path(__file__).resolve().parent
report = json.loads((root / 'snapshot.json').read_text())
archive = root / 'pair14-50.tar.gz'
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
old = json.loads((root.parent / 'brearcliffe-paper-rule-m-sarsa-snapshot-001/union-audit/audit.json').read_text())
runs = [r['directory'] for r in old['completed']] + [str(p) for p in sorted((extracted / 'runs').iterdir())]
repo = Path('/Users/relh/Code/workspace/sugarscape-brearcliffe/replications/brearcliffe_2020')
prepared = root.parent / 'brearcliffe-ensemble-preparation-001'
subprocess.run([sys.executable, str(repo / 'audit_ensemble.py'), str(prepared), str(root / 'union-audit'), *runs], check=True)
new = json.loads((root / 'union-audit/audit.json').read_text())
by_id = {r['run_id']: r for r in new['completed']}
assert len(by_id) == 952 and all(by_id[r['run_id']] == r for r in old['completed'])
(root / 'validation.json').write_text(json.dumps({'archive_members_verified': len(actual), 'new_inputs': 50, 'previous_inputs_preserved_exactly': 902, 'completed_inputs': 952, 'observations': new['observations'], 'pair14_complete': 50, 'scope': 'Full trajectories audited; paper comparison remains separate.'}, indent=2) + '\n')
subprocess.run([sys.executable, str(repo / 'summarize_cohort.py'), str(prepared), str(root / 'union-audit/audit.json'), str(root / 'cohort'), '--interpretation', 'released-code', '--pair-index', '14'], check=True)
