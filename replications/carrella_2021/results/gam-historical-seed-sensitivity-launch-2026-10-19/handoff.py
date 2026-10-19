from pathlib import Path
import hashlib
import json
import subprocess
import time

root = Path(__file__).resolve().parent
protocol = json.loads((root / 'protocol.json').read_text())
node = protocol['node']
remote = '/root/sugarscape/' + root.name
assert hashlib.sha256((root / 'payload.tar.gz').read_bytes()).hexdigest() == protocol['payload_sha256']

def call(name, command, timeout=90):
    result = subprocess.run(command, capture_output=True, text=True, timeout=timeout)
    (root / (name + '.json')).write_text(json.dumps({'command': command, 'exit_code': result.returncode, 'stdout': result.stdout, 'stderr': result.stderr}, indent=2) + '\n')
    assert result.returncode == 0, name
    return result.stdout

state = json.loads(call('node-preflight', ['autor', 'node', 'get', node, '--json']))
assert state['id'] == protocol['node_id'] and state['yours']
assert state['custom_image']['digest'] == 'sha256:fef68eaf0e829d464697948343ac440bbc189a0592b451eb99cddb46a8c8a7e3'
assert state['rate']['node_per_min_usd_micros'] <= protocol['node_rate_micros_per_minute_ceiling']
assert state['rate']['idle_window_minutes'] <= protocol['max_idle_minutes']
assert state['rate']['node_per_min_usd_micros'] * protocol['execution_export_idle_minutes_bound'] <= protocol['budget_usd_ceiling'] * 1000000
assert state['resources']['cpu_limit'] == 2 and state['resources']['memory_limit_bytes'] == 8589934592
commands = json.loads(call('commands-preflight', ['autor', 'ps', node, '--json']))
assert all(item['state'] != 'running' for item in commands['items'])
created = json.loads(call('mkdir', ['autor', 'run', node, '--timeout', '60', '--json', '--', 'mkdir', remote]))
assert created['exit_code'] == 0
prefix = root.name + '-input'
call('storage-upload', ['autor', 'storage', 'cp', str(root / 'payload.tar.gz'), 'relh-sugarscape-evidence-20261017/' + prefix + '/payload.tar.gz', '--json'], 180)
request = {'connection': 'storage/relh-sugarscape-evidence-20261017', 'source': 's3://relh-sugarscape-evidence-20261017/' + prefix + '/', 'dest_path': remote + '/staged-input'}
submission = json.loads(call('import-submission', ['autor', 'api', 'post', '/nodes/' + node + '/imports', '--data', json.dumps(request), '--json']))
deadline = time.monotonic() + 300
while True:
    status = json.loads(call('import-status', ['autor', 'api', 'get', '/nodes/' + node + '/imports/' + submission['import_id'], '--json']))
    if status['status'] == 'complete':
        assert status['bytes_transferred'] == protocol['payload_bytes']
        break
    assert status['status'] == 'running' and time.monotonic() < deadline
    time.sleep(10)
stage = 'cd ' + remote + ' && echo "' + protocol['payload_sha256'] + '  staged-input/payload.tar.gz" | sha256sum -c - && tar -xzf staged-input/payload.tar.gz && bash -n run.sh'
result = json.loads(call('stage', ['autor', 'run', node, '--timeout', '60', '--json', '--', 'bash', '-c', stage]))
assert result['exit_code'] == 0
submitted = json.loads(call('submission', ['autor', 'run', node, '--detach', '--timeout', '60', '--json', '--', 'timeout', '--kill-after=10', str(protocol['outer_seconds']), 'bash', remote + '/run.sh']))
print('Launched', submitted['command_id'], flush=True)
collector = root.parent / 'storage-handoff-20261017-001/collect_storage_api_bounded.py'
with (root / 'collector.log').open('x') as stream:
    result = subprocess.run(['/Users/relh/Code/workspace/sugarscape-replications/.venv/bin/python', str(collector), node, submitted['command_id'], root.name, '--terminal-file', remote + '/results.tar.gz', '--seconds', '24000', '--max-bytes', str(50 * 1024**2)], stdout=stream, stderr=subprocess.STDOUT, timeout=24200)
(root / 'handoff-terminal.json').write_text(json.dumps({'exit_code': result.returncode}, indent=2) + '\n')
assert result.returncode == 0
