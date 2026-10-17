from pathlib import Path
import hashlib
import json
import subprocess
import sys
import tarfile
import time

source = Path('/root/sugarscape/blueprints-portability-001')
root = Path('/root/sugarscape/blueprints-long5000-001')
root.mkdir()
(root / 'run.py').write_bytes(Path(__file__).read_bytes())
assert hashlib.sha256((source / 'run_runtime.py').read_bytes()).hexdigest() == 'df86e98f480c68abae4a3a647bcfe53bbce287c16850802e11c38eef8e6dd8d2'
commands = []
for model in ['rawSugarscape', 'altruisticHalfLookaheadBinary']:
    commands.append([str(source / 'venv/bin/python'), str(source / 'run_runtime.py'),
                     str(source / 'engine'), str(source / 'blueprints-runtimes.zip'),
                     model, '5000', str(root / model), '--seconds', '21600'])
plan = {'commands': commands, 'models': ['rawSugarscape', 'altruisticHalfLookaheadBinary'],
        'steps': 5000, 'indices_per_model': [0, 100], 'conditions': 200,
        'parallel_workers': 2, 'per_worker_seconds': 21600, 'source': str(source),
        'scope': 'Unstarted originalruntime5000step groups. Distinct from500step localgroups; no claimedpaper500seed reconstruction.'}
(root / 'plan.json').write_text(json.dumps(plan, indent=2) + '\n')
started = time.time()
processes = []
for index, command in enumerate(commands):
    with (root / f'worker-{index}.log').open('x') as log:
        processes.append(subprocess.Popen(command, stdout=log, stderr=subprocess.STDOUT))
statuses = [process.wait() for process in processes]
(root / 'terminal.json').write_text(json.dumps({'exit_codes': statuses, 'elapsed_seconds': time.time()-started})+'\n')
archive = Path('/root/sugarscape/blueprints-long5000-evidence-001.tar.gz')
with tarfile.open(archive, 'w:gz') as bundle:
    bundle.add(root, arcname='blueprints-long5000-001')
print(json.dumps({'archive': str(archive), 'sha256': hashlib.sha256(archive.read_bytes()).hexdigest(), 'exit_codes': statuses}), flush=True)
sys.exit(int(any(statuses)))
