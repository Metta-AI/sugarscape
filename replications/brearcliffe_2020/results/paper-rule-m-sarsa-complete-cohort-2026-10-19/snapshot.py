from pathlib import Path
import hashlib
import json
import subprocess
import sys
import tarfile
import time

root = Path('/root/sugarscape/brearcliffe-paper-table-ensemble-001')
output = Path(__file__).resolve().parent
runs = [root / 'batch/runs' / f'paper-table-pair-03-repeat-{i:02d}' for i in range(50)]
deadline = time.monotonic() + 600
while not all((p / 'terminal.json').is_file() for p in runs):
    assert time.monotonic() < deadline, 'Cohort remains incomplete after bounded observation'
    time.sleep(10)
assert all(p.is_dir() for p in runs)
assert all(json.loads((p / 'terminal.json').read_text())['exit_code'] == 0 for p in runs)
subprocess.run([sys.executable, str(root / 'payload/audit_ensemble.py'),
                str(root / 'prepared'), str(output / 'audit'), *map(str, runs)], check=True)
pins = {}
archive = output / 'paper-pair03-50.tar.gz'
with tarfile.open(archive, 'x:gz') as bundle:
    for run in runs:
        for path in sorted(run.rglob('*')):
            assert not path.is_symlink()
            if path.is_file():
                name = 'runs/' + run.name + '/' + str(path.relative_to(run))
                data = path.read_bytes()
                pins[name] = {'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()}
                bundle.add(path, arcname=name, recursive=False)
    bundle.add(output / 'audit', arcname='audit')
report = {'inputs': 50, 'archive_bytes': archive.stat().st_size,
          'archive_sha256': hashlib.sha256(archive.read_bytes()).hexdigest(), 'files': pins,
          'scope': 'Completed immutable input snapshot; the larger ensemble continues unchanged.'}
(output / 'snapshot.json').write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps({k:v for k,v in report.items() if k != 'files'}))
