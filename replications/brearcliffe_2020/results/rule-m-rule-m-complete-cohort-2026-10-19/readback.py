from pathlib import Path
import hashlib
import json
import shutil
import subprocess
import sys
import tarfile

root = Path(__file__).resolve().parent
archive = root / 'batch-results.tar.gz'
assert archive.stat().st_size == 6497867
assert hashlib.sha256(archive.read_bytes()).hexdigest() == '48380ec09f05a99dcff31135bcec4fd8e037b45fbc5f7d4a4adfdcf6b7276653'
assert shutil.disk_usage(root).free > 512 * 1024**2
extracted = root / 'readback'
extracted.mkdir()
with tarfile.open(archive) as bundle:
    for member in bundle:
        assert not Path(member.name).is_absolute() and '..' not in Path(member.name).parts
        assert member.isfile() or member.isdir()
    bundle.extractall(extracted, filter='data')
pins = {}
with tarfile.open(archive) as bundle:
    for member in bundle:
        if member.isfile():
            assert member.name not in pins
            data = bundle.extractfile(member).read()
            assert data == (extracted / member.name).read_bytes()
            pins[member.name] = hashlib.sha256(data).hexdigest()
assert json.loads((extracted / 'wrapper-terminal.json').read_text())['batch_exit_code'] == 0
terminal = json.loads((extracted / 'batch/terminal.json').read_text())
assert terminal['successful_inputs'] == terminal['attempted_inputs'] == 8
assert terminal['unstarted_inputs'] == 0 and terminal['exit_code'] == 0
new_runs = sorted((extracted / 'batch/runs').iterdir())
assert [p.name for p in new_runs] == [f'released-code-pair-00-repeat-{i}' for i in range(42, 50)]
old = json.loads((root.parent / 'brearcliffe-rule-m-ec-snapshot-001/union-audit/audit.json').read_text())
runs = [r['directory'] for r in old['completed']] + list(map(str, new_runs))
repo = Path('/Users/relh/Code/workspace/sugarscape-brearcliffe/replications/brearcliffe_2020')
prepared = root.parent / 'brearcliffe-ensemble-preparation-001'
subprocess.run([sys.executable, str(repo / 'audit_ensemble.py'), str(prepared), str(root / 'union-audit'), *runs], check=True)
new = json.loads((root / 'union-audit/audit.json').read_text())
by_id = {r['run_id']: r for r in new['completed']}
assert len(by_id) == 102 and all(by_id[r['run_id']] == r for r in old['completed'])
(root / 'readback-validation.json').write_text(json.dumps({'archive_members_verified': len(pins), 'archive_sha256': hashlib.sha256(archive.read_bytes()).hexdigest(), 'new_inputs': 8, 'previous_inputs_preserved_exactly': 94, 'completed_inputs': 102, 'observations': new['observations'], 'pair00_complete': 50, 'members_sha256': pins, 'scope': 'Archive readback and full trajectory audit; paper comparison remains separate.'}, indent=2) + '\n')
subprocess.run([sys.executable, str(repo / 'summarize_cohort.py'), str(prepared), str(root / 'union-audit/audit.json'), str(root / 'cohort'), '--interpretation', 'released-code', '--pair-index', '0'], check=True)
