"""Run eight sequential original trajectories under two pinned interpreters."""
from pathlib import Path
import hashlib
import json
import os
import subprocess
import signal
import sys
import tarfile
import time

root = Path(__file__).resolve().parent
plan = json.loads((root / 'protocol.json').read_text())
engine = root / 'engine'
interpreters = {'cpython': root / 'cpython/bin/python', 'pypy': root / 'pypy/pypy3.11-v7.3.20-linux64/bin/pypy3'}
versions = {name: subprocess.check_output([str(path), '--version'], text=True).strip() for name, path in interpreters.items()}
assert '3.11.14' in versions['cpython']
assert '3.11.13' in versions['pypy'] and '7.3.20' in versions['pypy']
(root / 'versions.json').write_text(json.dumps(versions, indent=2) + '\n')
for name, digest in plan['source_sha256'].items():
    assert hashlib.sha256((engine / name).read_bytes()).hexdigest() == digest
signal.signal(signal.SIGTERM, lambda signum, frame: sys.exit(128 + signum))
results = []
started = time.monotonic()
try:
    for condition in plan['conditions']:
        original = root / condition['entry']
        assert hashlib.sha256(original.read_bytes()).hexdigest() == condition['configuration_sha256']
        for index, runtime in enumerate(plan['order']):
            out = root / 'runs' / (condition['entry'].removesuffix('.config') + f'-{index}-{runtime}')
            out.mkdir(parents=True)
            config = json.loads(original.read_text())
            config['logfile'] = str(out / 'trajectory.json')
            (out / 'config.json').write_text(json.dumps(config, indent=2) + '\n')
            command = ['/usr/bin/time', '-v', '-o', str(out / 'memory.log'), str(interpreters[runtime]), str(engine / 'sugarscape.py'), '--conf', str(out / 'config.json')]
            (out / 'command.json').write_text(json.dumps(command, indent=2) + '\n')
            remaining = plan['maximum_simulation_seconds'] - (time.monotonic() - started)
            assert remaining > 0
            before = time.monotonic()
            with (out / 'stdout.log').open('w') as stdout, (out / 'stderr.log').open('w') as stderr:
                process = subprocess.Popen(command, cwd=engine, env=os.environ | {'PYTHONHASHSEED': '0', 'PYTHONDONTWRITEBYTECODE': '1'}, stdout=stdout, stderr=stderr, start_new_session=True)
                try:
                    returncode = process.wait(timeout=remaining)
                finally:
                    if process.poll() is None:
                        os.killpg(process.pid, signal.SIGKILL)
                        process.wait()
            elapsed = time.monotonic() - before
            (out / 'exit.json').write_text(json.dumps({'exit_code': returncode}) + '\n')
            assert returncode == 0
            trajectory = (out / 'trajectory.json').read_bytes()
            digest = hashlib.sha256(trajectory).hexdigest()
            assert digest == condition['expected_trajectory_sha256']
            records = json.loads(trajectory)
            assert len(records) == plan['observations']
            assert [r['timestep'] for r in records] == list(range(5001))
            for name, expected in plan['source_sha256'].items():
                assert hashlib.sha256((engine / name).read_bytes()).hexdigest() == expected
            record = {'entry': condition['entry'], 'runtime': runtime, 'order': index, 'elapsed_seconds': elapsed, 'trajectory_sha256': digest, 'observations': len(records), 'final_population': records[-1]['population']}
            results.append(record)
            with (root / 'completed.jsonl').open('a') as ledger:
                ledger.write(json.dumps(record) + '\n')
            print(json.dumps(record), flush=True)
    assert len(results) == 8
    (root / 'complete.json').write_text(json.dumps({'runs': results, 'versions': versions, 'scope': plan['scope']}, indent=2) + '\n')
finally:
    target = root / 'terminal-evidence.tar.gz'
    with tarfile.open(target, 'w:gz') as archive:
        for path in sorted(root.iterdir()):
            if path.name not in {'engine', 'cpython', 'pypy', 'pypy.tar.bz2', 'terminal-evidence.tar.gz', 'payload.tar.gz'}:
                archive.add(path, arcname=path.name)
    print(json.dumps({'archive': str(target), 'bytes': target.stat().st_size, 'sha256': hashlib.sha256(target.read_bytes()).hexdigest(), 'completed': len(results)}), flush=True)
