"""Collect only the completed prospective pair and audit every saved fold."""
from pathlib import Path
import hashlib
import json
import os
import subprocess
import tarfile
import time

root = Path(__file__).resolve().parent
node = 'relh-sugarscape-carrella-r405-cpu2-20261019-v1'
command = 'cmd-ewzp3'
deadline = time.monotonic() + 600
while True:
    state = json.loads(subprocess.check_output(['autor', 'ps', node, '--json']))
    row = next(x for x in state['items'] if x['command_id'] == command)
    if row['state'] == 'exited':
        assert row['exit_code'] == 0
        break
    assert row['state'] == 'running' and time.monotonic() < deadline
    time.sleep(20)
receipt = json.loads(subprocess.check_output(['autor', '--json', 'api', 'get', f'/nodes/{node}/commands/{command}?offset=0']))
(root / 'snapshot-command.json').write_text(json.dumps(receipt, indent=2) + '\n')
assert not receipt['truncated']
lines = receipt['output'].splitlines()
expected_bytes = int(lines[-2])
expected_hash = lines[-1].split()[0]
archive = root / 'results.tar.gz'
process = subprocess.run(['autor', 'cp', node + ':/root/sugarscape/' + root.name + '/results.tar.gz', str(archive), '--json'], capture_output=True, text=True, timeout=120)
(root / 'download.json').write_text(process.stdout)
assert process.returncode == 0, process.stderr
assert archive.stat().st_size == expected_bytes
assert hashlib.sha256(archive.read_bytes()).hexdigest() == expected_hash
native = root / 'native'
native.mkdir()
payload = root.parent / 'carrella-gam-historical-seeds-001/payload'
with tarfile.open(archive) as tar:
    members = tar.getmembers()
    assert len({x.name for x in members}) == len(members)
    assert all(x.isfile() or x.isdir() for x in members)
    assert all(not Path(x.name).is_absolute() and '..' not in Path(x.name).parts for x in members)
    hashes = {x.name: {'bytes': x.size, 'sha256': hashlib.sha256(tar.extractfile(x).read()).hexdigest()} for x in members if x.isfile()}
    tar.extractall(native, filter='data')
assert len(hashes) == 35
fixed = [name for name in hashes if (payload / name).is_file()]
assert len(fixed) == 9
for name in fixed:
    assert (native / name).read_bytes() == (payload / name).read_bytes()
for name, metadata in hashes.items():
    assert hashlib.sha256((native / name).read_bytes()).hexdigest() == metadata['sha256']
for seed in (7, 8):
    assert json.loads((native / f'seed-{seed:02d}/terminal.json').read_text())['exit_code'] == 0
(root / 'readback.json').write_text(json.dumps({'receipt': {'bytes': expected_bytes, 'sha256': expected_hash}, 'members': hashes, 'frozen_payload_members_exact': fixed, 'completed_seeds': [7,8], 'scope': 'Prospective seeds7/8 complete; nine-seed batch still incomplete.'}, indent=2) + '\n')
study = root.parent.parent / 'sugarscape-carrella/replications/carrella_2021'
env = dict(os.environ, R_LIBS_USER=str(root.parent.parent / 'sugarscape-replication-tools/R-library'))
for seed in (7,8):
    cmd = ['/opt/homebrew/bin/Rscript', '--vanilla', str(study / 'audit_replayed_gam.R'), str(native / 'inputs'), str(native / f'seed-{seed:02d}/run'), str(study / 'published_table8.json'), str(root / f'audit-{seed:02d}')]
    p = subprocess.run(cmd, capture_output=True, text=True, env=env, timeout=120)
    (root / f'audit-{seed:02d}-command.json').write_text(json.dumps({'command': cmd, 'exit_code': p.returncode, 'stdout': p.stdout, 'stderr': p.stderr}, indent=2) + '\n')
    assert p.returncode == 0, p.stderr
cmd = ['/opt/homebrew/bin/Rscript', '--vanilla', str(root / 'compare_seed0.R'), str(root.parent / 'carrella-gam-historical-full-readback-001/native/run'), str(native), str(root / 'seed0-comparison.json')]
p = subprocess.run(cmd, capture_output=True, text=True, env=env, timeout=120)
(root / 'comparison-command.json').write_text(json.dumps({'command': cmd, 'exit_code': p.returncode, 'stdout': p.stdout, 'stderr': p.stderr}, indent=2) + '\n')
assert p.returncode == 0, p.stderr
print(p.stdout, flush=True)
