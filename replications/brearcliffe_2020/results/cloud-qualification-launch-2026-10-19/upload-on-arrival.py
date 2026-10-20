import hashlib
import json
import subprocess
import time
from pathlib import Path

root = Path(__file__).resolve().parent
node = 'relh-sugarscape-brearcliffe-cpu8-20261019-v1'
bundle = json.loads((root / 'bundle.json').read_text())
assert hashlib.sha256((root / 'trial-input.tar.gz').read_bytes()).hexdigest() == bundle['sha256']
started = time.monotonic()
while time.monotonic() - started < 8 * 3600:
    process = subprocess.run(['autor', 'node', 'get', node, '--json'], capture_output=True, text=True, check=True, timeout=120)
    state = json.loads(process.stdout)
    with (root / 'arrival-polls.jsonl').open('a') as file:
        file.write(json.dumps({'elapsed_seconds': time.monotonic() - started, 'state': state['status']}) + '\n')
    if state['status'] == 'running':
        assert state['rate']['node_per_min_usd_micros'] <= 12000
        assert state['rate']['idle_window_minutes'] <= 15
        upload = subprocess.run(['autor', 'cp', str(root / 'trial-input.tar.gz'),
                                 node + ':/root/sugarscape/brearcliffe-cloud-qualification-001/trial-input.tar.gz', '--json'],
                                capture_output=True, text=True, timeout=240)
        (root / 'upload-terminal.json').write_text(json.dumps({'exit_code': upload.returncode, 'stdout': upload.stdout,
                                                              'stderr': upload.stderr}, indent=2) + '\n')
        assert upload.returncode == 0
        print('Verified bundle uploaded to the owned trial node.', flush=True)
        break
    assert state['status'] in ['queued', 'provisioning', 'starting', 'pulling'], state['status']
    time.sleep(60)
else:
    raise RuntimeError('Arrival upload deadline exceeded; inspect node and boot command before retrying.')
