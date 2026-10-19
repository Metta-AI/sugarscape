"""Compare six complete native trajectories across two pinned Python runtimes."""

from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tarfile
import time
import urllib.request

root = Path(__file__).resolve().parent
base = Path('/root/sugarscape/blueprints-selfishness037-batch-001')
plan = json.loads((root / 'protocol.json').read_bytes())
for name, digest in plan['frozen_files'].items():
    assert hashlib.sha256((root / name).read_bytes()).hexdigest() == digest
assert float(os.environ['GMN_CPU_LIMIT']) >= 8
interpreters = {
    'cpython': base / 'cpython/bin/python',
    'pypy': base / 'pypy/pypy3.11-v7.3.20-linux64/bin/pypy3',
}
versions = {
    key: subprocess.check_output([str(path), '-c', 'import sys; print(sys.version)'], text=True).strip()
    for key, path in interpreters.items()
}
assert versions['cpython'].startswith('3.11.14')
assert versions['pypy'].startswith('3.11.13') and 'PyPy 7.3.20' in versions['pypy']
(root / 'versions.json').write_text(json.dumps(versions, indent=2) + '\n')
archive = root / 'original-heterogeneous.zip'
assert not archive.exists()
with urllib.request.urlopen(plan['archive_url'], timeout=300) as response:
    raw = response.read()
assert hashlib.sha256(raw).hexdigest() == plan['archive_sha256']
archive.write_bytes(raw)
for directory in ['runs', 'audits', 'logs']:
    (root / directory).mkdir()
started = time.monotonic()


def execute(job):
    """Execute and audit one full native workflow, retaining nonzero receipts."""
    row, runtime = job
    name = row['entry'].removesuffix('.config') + '-' + runtime
    target = root / 'runs' / name
    command = ['/usr/bin/timeout', '--signal=TERM', '--kill-after=15', '5400',
               sys.executable, str(root / 'run_supplement.py'), str(base / 'engine'),
               str(archive), 'heterogeneous', row['entry'], str(target),
               '--interpreter', str(interpreters[runtime])]
    with (root / 'logs' / (name + '.log')).open('x') as log:
        result = subprocess.run(command, stdout=log, stderr=subprocess.STDOUT)
        record = {'entry': row['entry'], 'runtime': runtime, 'exit_code': result.returncode,
                  'command': command, 'directory': name}
        if result.returncode == 0:
            audit_command = [sys.executable, str(root / 'audit_supplement.py'), str(archive),
                             str(target), str(root / 'audits' / name), '--expected-runtime', runtime]
            audit = subprocess.run(audit_command, stdout=log, stderr=subprocess.STDOUT, timeout=180)
            record['audit_exit_code'] = audit.returncode
            if audit.returncode == 0:
                record['result'] = json.loads((target / 'result.json').read_bytes())
                assert hashlib.sha256((target / 'original.config').read_bytes()).hexdigest() == row['configuration_sha256']
        (root / 'logs' / (name + '.receipt.json')).write_text(json.dumps(record, indent=2) + '\n')
    return record


jobs = [(row, runtime) for row in plan['inputs'] for runtime in interpreters]
assert len(jobs) == 6
with ThreadPoolExecutor(max_workers=6) as pool:
    records = list(pool.map(execute, jobs))
success = all(r['exit_code'] == 0 and 'result' in r for r in records)
comparisons = []
if success:
    for row in plan['inputs']:
        pair = [r for r in records if r['entry'] == row['entry']]
        trajectories = [(root / 'runs' / r['directory'] / 'trajectory.json').read_bytes() for r in pair]
        comparisons.append({'entry': row['entry'], 'byte_identical': trajectories[0] == trajectories[1],
                            'sha256': [hashlib.sha256(raw).hexdigest() for raw in trajectories]})
summary = {'all_runs_audited': success, 'comparisons': comparisons, 'records': records,
           'elapsed_seconds': time.monotonic() - started,
           'scope': 'Three original configurations only; concurrent timing is not isolated throughput or whole-sweep equivalence.'}
(root / 'summary.json').write_text(json.dumps(summary, indent=2) + '\n')
files = [p for p in root.rglob('*') if p.is_file() and p != archive]
assert sum(p.stat().st_size for p in files) < 1024**3
sealed = root / 'terminal-evidence.tar.gz'
with tarfile.open(sealed, 'x:gz') as tar:
    for path in sorted(files):
        tar.add(path, arcname=str(path.relative_to(root)), recursive=False)
print('SNAPSHOT ' + json.dumps({'archive': str(sealed), 'bytes': sealed.stat().st_size,
                              'sha256': hashlib.sha256(sealed.read_bytes()).hexdigest()}), flush=True)
assert success and all(row['byte_identical'] for row in comparisons)
