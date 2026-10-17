from pathlib import Path
import gzip
import hashlib
import json
import os
import shutil
import subprocess
import sys
import time
import zipfile

root = Path(__file__).resolve().parent
base = root.parent
engine = base.parent / 'sugarscape-dtl-blueprints-reference'
archive_path = base / 'papers/blueprints-runtimes.zip'
release = 'b9ca671ab7591c7b3606f2d76c33eda344d626d1'
assert subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=engine, text=True).strip() == release
assert not subprocess.check_output(['git', 'status', '--porcelain', '--untracked-files=no'], cwd=engine, text=True).strip()
archive_hash = hashlib.sha256(archive_path.read_bytes()).hexdigest()
assert archive_hash == '43b1967e9af9d7aac9785258706fd5abec6257235940b85aa811519c0e6ae98a'
with zipfile.ZipFile(archive_path) as archive:
    inputs = {name: archive.read(name) for name in archive.namelist()
              if name.startswith('500-rawSugarscape')}
entries = sorted(inputs)
assert len(entries) == 100 and len({json.loads(raw)['seed'] for raw in inputs.values()}) == 100
assert entries[0] == '500-rawSugarscape1071049487305188627.config'
pilot = json.loads((base / 'blueprints-runtime-pilot-001/audit.json').read_text())
assert pilot['entry'] == entries[0] and pilot['final_timestep'] == 500
source_hashes = {path.name: hashlib.sha256(path.read_bytes()).hexdigest() for path in sorted(engine.glob('*.py'))}
pins = json.loads((base.parent / 'sugarscape-blueprints/replications/blueprints_2024/source-sha256.json').read_text())
assert source_hashes == pins['source_sha256']
manifest = {'release': release, 'archive_sha256': archive_hash, 'entries': entries[1:],
            'start': 1, 'stop': 100, 'order': 'lexicographic archive filename',
            'completed_pilot_excluded': entries[0], 'source_sha256': source_hashes,
            'python': sys.version, 'pythonhashseed': '0', 'model': 'rawSugarscape', 'timesteps': 500,
            'timeout_seconds': 7200, 'per_condition_timeout_seconds': 1800,
            'runner_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            'scope': 'Remaining99original raw500 runtime-archive inputs. Not homogeneous seeds or claimed500seed Table6.'}
with (root / 'manifest.json').open('x') as stream:
    stream.write(json.dumps(manifest, indent=2) + '\n')
started = time.monotonic()
with (root / 'completed.jsonl').open('x') as ledger:
    for index, entry in enumerate(entries[1:], 1):
        remaining = 7200 - (time.monotonic() - started)
        assert remaining > 0 and shutil.disk_usage(root).free >= 2 * 1024**3
        assert all(hashlib.sha256((engine / name).read_bytes()).hexdigest() == digest for name, digest in source_hashes.items())
        output = root / entry.removesuffix('.config')
        output.mkdir()
        original = inputs[entry]
        config = json.loads(original)
        assert config['timesteps'] == 500 and config['agentDecisionModels'] == ['rawSugarscape']
        assert config['headlessMode'] and config['startingAgents'] == 250
        assert config.keys() == json.loads((engine / 'config.json').read_text())['sugarscapeOptions'].keys()
        (output / 'original.config').write_bytes(original)
        config['logfile'] = str(output / 'trajectory.json')
        (output / 'config.json').write_text(json.dumps(config, indent=2) + '\n')
        command = [sys.executable, str(engine / 'sugarscape.py'), '--conf', str(output / 'config.json')]
        (output / 'command.json').write_text(json.dumps(command) + '\n')
        condition_started = time.monotonic()
        with (output / 'stdout.log').open('x') as stdout, (output / 'stderr.log').open('x') as stderr:
            result = subprocess.run(command, cwd=engine, env={**os.environ, 'PYTHONHASHSEED': '0', 'PYTHONDONTWRITEBYTECODE': '1'},
                                    stdout=stdout, stderr=stderr, timeout=min(remaining, 1800))
        (output / 'exit.json').write_text(json.dumps({'exit_code': result.returncode}) + '\n')
        result.check_returncode()
        raw = (output / 'trajectory.json').read_bytes()
        rows = json.loads(raw)
        assert [row['timestep'] for row in rows] == list(range(len(rows)))
        assert rows[-1]['timestep'] == 500 or rows[-1]['population'] == 0
        compressed = gzip.compress(raw, mtime=0)
        assert gzip.decompress(compressed) == raw
        (output / 'trajectory.json.gz').write_bytes(compressed)
        record = {'index': index, 'entry': entry, 'seed': config['seed'], 'exit_code': 0,
                  'observations': len(rows), 'final_timestep': rows[-1]['timestep'], 'final_population': rows[-1]['population'],
                  'elapsed_seconds': time.monotonic() - condition_started,
                  'files_sha256': {path.name: hashlib.sha256(path.read_bytes()).hexdigest() for path in sorted(output.iterdir())}}
        ledger.write(json.dumps(record) + '\n')
        ledger.flush()
        print(index, entry, record['final_population'], flush=True)
(root / 'complete.json').write_text(json.dumps({'completed_runs': 99}) + '\n')
