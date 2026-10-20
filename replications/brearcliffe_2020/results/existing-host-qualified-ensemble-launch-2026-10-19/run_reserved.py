"""Run only the reserved ensemble after exact host qualification; retain all attempts."""
from pathlib import Path
import hashlib
import json
import subprocess
import sys
import tarfile
import time

root = Path(__file__).resolve().parent
qualification = root.parent / 'brearcliffe-existing-host-qualification-001' / 'payload'
summary = json.loads((qualification / 'results/summary.json').read_text())
assert summary['exit_code'] == 0
cases = json.loads((qualification / 'cases.json').read_text())
assert {case['name'] for case in cases} == {'rule-m-ec', 'q-sarsa'}
assert {case['case'] for case in summary['cases']} == {'rule-m-ec', 'q-sarsa'}
for case in cases:
    comparison = json.loads((qualification / 'results' / case['name'] / 'comparison.json').read_text())
    assert comparison['observations'] == 20001 and comparison['compared_fields'] == 320016
    assert comparison['differences'] == []
    actual = qualification / 'results' / case['name'] / 'trajectory.csv'
    assert hashlib.sha256(actual.read_bytes()).hexdigest() == case['sha256']
    assert actual.read_bytes() == (qualification / case['reference']).read_bytes()
for name, digest in json.loads((qualification / 'payload-sha256.json').read_text()).items():
    assert hashlib.sha256((qualification / name).read_bytes()).hexdigest() == digest
payload = root / 'payload'
for name, digest in json.loads((payload / 'payload-sha256.json').read_text()).items():
    assert hashlib.sha256((payload / name).read_bytes()).hexdigest() == digest
plan = json.loads((root / 'execution-plan.json').read_text())
assert plan['workers'] == 8 and plan['max_inputs'] == 749
assert plan['wall_seconds'] == 41400 and plan['per_run_seconds'] == 1800
assert not (root / 'batch').exists()
command = [sys.executable, str(payload / 'run_ensemble_batch.py'), str(root / 'prepared'),
           str(payload / 'assignment.csv'), str(qualification / 'assets'), str(qualification / 'app'),
           str(root / 'batch'), '--java', '/usr/bin/java', '--interpretation', 'released-code',
           '--workers', str(plan['workers']), '--max-inputs', str(plan['max_inputs']),
           '--wall-seconds', str(plan['wall_seconds']), '--per-run-seconds', str(plan['per_run_seconds'])]
(root / 'batch-command.json').write_text(json.dumps(command, indent=2) + '\n')
started = time.monotonic()
process = subprocess.run(command)
(root / 'wrapper-terminal.json').write_text(json.dumps({'batch_exit_code': process.returncode,
    'elapsed_seconds': time.monotonic() - started, 'scope': 'All attempts retained; independent audit required.'}, indent=2) + '\n')
archive = root / 'batch-results.tar.gz'
with tarfile.open(archive, 'w:gz') as tar:
    for name in ['batch', 'execution-plan.json', 'batch-command.json', 'wrapper-terminal.json', 'run_reserved.py']:
        tar.add(root / name, arcname=name)
assert archive.stat().st_size <= 2 * 1024**3
print('SNAPSHOT ' + json.dumps({'archive': str(archive), 'bytes': archive.stat().st_size,
      'sha256': hashlib.sha256(archive.read_bytes()).hexdigest()}), flush=True)
sys.exit(process.returncode)
