from pathlib import Path
import hashlib
import json
import os
import subprocess
import sys
import time

root = Path(__file__).resolve().parent
assert not (root / 'transfer').exists()
with (root / 'transfer-watcher-start.json').open('x') as f:
    json.dump({'pid': os.getpid(), 'started_unix': time.time(), 'max_wait_seconds': 18000}, f, indent=2)
started = time.monotonic()
pins = json.loads((root / 'transfer-pins.json').read_bytes())
while not (root / 'terminal.json').exists():
    producer = json.loads((root / 'started.json').read_bytes())['pid']
    live = subprocess.run(['/bin/ps', '-p', str(producer), '-o', 'command='], capture_output=True, text=True)
    assert live.returncode == 0 and str(root / 'run_frontier_campaign.py') in live.stdout
    assert time.monotonic() - started < 18000
    time.sleep(60)
terminal = json.loads((root / 'terminal.json').read_bytes())
plan = json.loads((root / 'plan.json').read_bytes())
assert terminal['all_complete'] and terminal['completed'] == [j['name'] for j in plan['jobs']]
for name, digest in pins.items():
    assert hashlib.sha256((root / name).read_bytes()).hexdigest() == digest
for job in plan['jobs']:
    folder = root / job['name']
    assert json.loads((folder / 'terminal.json').read_bytes())['exit_code'] == 0
    assert json.loads((folder / 'audit.json').read_bytes())['native_runs'] == job['native_runs']
with (root / 'transfer.log').open('x') as log:
    result = subprocess.run([sys.executable, str(root / 'run_frontier_transfer.py'), str(root / 'transfer-plan.json'), str(root / 'transfer')],
                            stdout=log, stderr=subprocess.STDOUT, timeout=18 * 1860 + 120)
(root / 'transfer-terminal.json').write_text(json.dumps({'exit_code': result.returncode, 'ended_unix': time.time()}, indent=2) + '\n')
assert result.returncode == 0
with (root / 'transfer-audit.log').open('x') as log:
    result = subprocess.run([sys.executable, str(root / 'audit_frontier_transfer.py'), str(root / 'transfer'), str(root / 'transfer-audit.json')],
                            stdout=log, stderr=subprocess.STDOUT, timeout=300)
(root / 'transfer-audit-terminal.json').write_text(json.dumps({'exit_code': result.returncode}, indent=2) + '\n')
assert result.returncode == 0
