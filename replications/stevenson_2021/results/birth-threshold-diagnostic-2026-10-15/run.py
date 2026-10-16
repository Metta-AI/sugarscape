import hashlib
import json
from pathlib import Path
import subprocess
import time

root = Path(__file__).resolve().parent
with (root / 'completed.jsonl').open('x') as completed:
    for seed in range(101, 111):
        for variant in ['baseline', 'strict']:
            path = root / f'{variant}-{seed}.csv'
            command = [str(root / variant), str(seed), '10', '40', '100000']
            started = time.monotonic()
            with path.open('x') as stdout, path.with_suffix('.stderr').open('x') as stderr:
                subprocess.run(command, stdout=stdout, stderr=stderr, check=True)
            completed.write(json.dumps({'seed':seed,'variant':variant,'command':command,
                'elapsed_seconds':time.monotonic()-started,
                'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})+'\n')
            completed.flush()
            print(variant, seed, 'completed', flush=True)
