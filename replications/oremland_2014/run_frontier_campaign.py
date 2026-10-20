"""Run a frozen, bounded optimizer campaign without retries or duplicate outputs."""
import argparse
from contextlib import ExitStack
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('plan', type=Path)
args = parser.parse_args()
root = args.plan.resolve().parent
plan = json.loads(args.plan.read_bytes())
source = Path(__file__).resolve().parent
for filename, key in [('run_optimizer.py', 'runner_sha256'), ('audit_optimizer.py', 'auditor_sha256')]:
    assert hashlib.sha256((source / filename).read_bytes()).hexdigest() == plan[key]
assert len({job['name'] for job in plan['jobs']}) == len(plan['jobs'])
assert plan['workers'] == 2
for job in plan['jobs']:
    folder = root / job['name']
    assert not (folder / 'run').exists() and not (folder / 'start.json').exists()
    manifest = json.loads(Path(job['manifest']).read_bytes())
    model = Path(manifest['command'][-3])
    assert hashlib.sha256(model.read_bytes()).hexdigest() == manifest['model_sha256']
    assert hashlib.sha256(model.with_name('sugar-map.txt').read_bytes()).hexdigest() == manifest['landscape_sha256']
with (root / 'started.json').open('x') as file:
    json.dump({'pid': os.getpid(), 'started_unix': time.time(), 'plan_sha256': hashlib.sha256(args.plan.read_bytes()).hexdigest()}, file, indent=2)
started = time.monotonic()
completed = []
for offset in range(0, len(plan['jobs']), plan['workers']):
    if time.monotonic() - started >= plan['admission_seconds']:
        break
    wave = plan['jobs'][offset:offset + plan['workers']]
    processes = []
    with ExitStack() as stack:
        for job in wave:
            folder = root / job['name']
            command = ['/opt/homebrew/bin/gtimeout', '--signal=TERM', f"--kill-after={plan['kill_after_seconds']}",
                       str(plan['job_seconds']), sys.executable, str(source / 'run_optimizer.py'),
                       job['manifest'], job['protocol'], str(folder / 'run')]
            log = stack.enter_context((folder / 'optimizer.log').open('x'))
            process = subprocess.Popen(command, stdout=log, stderr=subprocess.STDOUT)
            (folder / 'start.json').write_text(json.dumps({'pid': process.pid, 'command': command, 'started_unix': time.time()}, indent=2) + '\n')
            processes.append((job, process))
        exits = [(job, process.wait()) for job, process in processes]
    for job, code in exits:
        folder = root / job['name']
        (folder / 'terminal.json').write_text(json.dumps({'exit_code': code, 'ended_unix': time.time()}, indent=2) + '\n')
    assert all(code == 0 for _, code in exits), 'Failed wave retained; no automatic retry or subsequent launch.'
    for job, _ in exits:
        folder = root / job['name']
        with (folder / 'audit.log').open('x') as log:
            result = subprocess.run([sys.executable, str(source / 'audit_optimizer.py'), str(folder / 'run'), str(folder / 'audit.json')],
                                    stdout=log, stderr=subprocess.STDOUT, timeout=120)
        assert result.returncode == 0
        completed.append(job['name'])
    (root / 'progress.json').write_text(json.dumps({'completed': completed, 'elapsed_seconds': time.monotonic() - started}, indent=2) + '\n')
(root / 'terminal.json').write_text(json.dumps({'completed': completed, 'planned': len(plan['jobs']),
                                              'all_complete': len(completed) == len(plan['jobs']),
                                              'elapsed_seconds': time.monotonic() - started}, indent=2) + '\n')
