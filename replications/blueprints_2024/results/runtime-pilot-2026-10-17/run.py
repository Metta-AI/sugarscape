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
assert shutil.disk_usage(root).free >= 2 * 1024**3
assert hashlib.sha256(archive_path.read_bytes()).hexdigest() == '43b1967e9af9d7aac9785258706fd5abec6257235940b85aa811519c0e6ae98a'
entry = '500-rawSugarscape1071049487305188627.config'
with zipfile.ZipFile(archive_path) as archive:
    original = archive.read(entry)
configuration = json.loads(original)
assert configuration['seed'] == 1071049487305188627
assert configuration['timesteps'] == 500
assert configuration['agentDecisionModels'] == ['rawSugarscape']
assert configuration.keys() == json.loads((engine / 'config.json').read_text())['sugarscapeOptions'].keys()
assert not (root / 'manifest.json').exists()
(root / 'original.config').write_bytes(original)
configuration['logfile'] = str(root / 'trajectory.json')
(root / 'config.json').write_text(json.dumps(configuration, indent=2) + '\n')
command = [sys.executable, str(engine / 'sugarscape.py'), '--conf', str(root / 'config.json')]
pins = json.loads((base.parent / 'sugarscape-blueprints/replications/blueprints_2024/source-sha256.json').read_text())
source_hashes = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(engine.glob('*.py'))}
assert source_hashes == pins['source_sha256']
manifest = {'release': release, 'archive_sha256': hashlib.sha256(archive_path.read_bytes()).hexdigest(),
            'entry': entry, 'selection': 'Lexicographically first archived rawSugarscape500step filename, selected before results.',
            'source_sha256': source_hashes, 'original_config_sha256': hashlib.sha256(original).hexdigest(),
            'config_sha256': hashlib.sha256((root / 'config.json').read_bytes()).hexdigest(),
            'command': command, 'python': sys.version, 'pythonhashseed': '0', 'timeout_seconds': 1800,
            'changes': {'logfile': {'original': json.loads(original)['logfile'], 'effective': configuration['logfile']}},
            'scope': 'One deposited runtime-archive input, disjoint from homogeneous seeds; not a500seed Table6 replication.'}
(root / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
started = time.monotonic()
with (root / 'stdout.log').open('x') as stdout, (root / 'stderr.log').open('x') as stderr:
    result = subprocess.run(command, cwd=engine, env={**os.environ, 'PYTHONHASHSEED': '0', 'PYTHONDONTWRITEBYTECODE': '1'},
                            stdout=stdout, stderr=stderr, timeout=1800)
(root / 'exit.json').write_text(json.dumps({'exit_code': result.returncode, 'elapsed_seconds': time.monotonic()-started})+'\n')
result.check_returncode()
raw = (root / 'trajectory.json').read_bytes()
compressed = gzip.compress(raw, mtime=0)
assert gzip.decompress(compressed) == raw
(root / 'trajectory.json.gz').write_bytes(compressed)
print(json.dumps({'raw_bytes': len(raw), 'gzip_bytes': len(compressed)}))
