"""Execute one frozen full-length ensemble input without overwriting prior evidence."""

import argparse
import csv
import hashlib
import json
import math
import shutil
import subprocess
import time
from pathlib import Path

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('prepared', type=Path)
parser.add_argument('run_id')
parser.add_argument('runtime_assets', type=Path, help='Qualified Replay.class, map, and matrix directory')
parser.add_argument('netlogo_app', type=Path, help='NetLogo 6.1.1 application JAR directory')
parser.add_argument('new_output', type=Path)
parser.add_argument('--java', required=True)
parser.add_argument('--timeout-seconds', type=int, default=600)
args = parser.parse_args()
assert 0 < args.timeout_seconds <= 3600
assert shutil.disk_usage(args.new_output.parent).free > 2 * 1024**3
summary = json.loads((args.prepared / 'summary.json').read_text())
manifest = args.prepared / 'manifest.csv'
assert hashlib.sha256(manifest.read_bytes()).hexdigest() == summary['manifest_sha256']
with manifest.open() as file:
    selected = [row for row in csv.DictReader(file) if row['run_id'] == args.run_id]
assert len(selected) == 1
row = selected[0]
assert row['steps'] == '20000'
model = args.prepared / row['model']
assert hashlib.sha256(model.read_bytes()).hexdigest() == row['model_sha256']
expected_assets = {
    'Replay.class': 'fa3d53b229521c7a8836278dbb25a450c80ae4199bff07649a0a226dd6a7b30b',
    'symmetric-sugar-map.txt': 'b36a8a31d804198683d30a29217d1e08830bd04ac539fa2c7250bb3168d3ba9a',
    'matrix/matrix.jar': '96ebe1795462e511301eee35d43067959b32da9bfec1c4ff5cad980dc58953d0',
    'matrix/jama-1.0.3.jar': 'c7325ee29be1aac1287ddac690f73671f1cd911ca9eca7c619990e86310556fd',
}
for name, digest in expected_assets.items():
    assert hashlib.sha256((args.runtime_assets / name).read_bytes()).hexdigest() == digest, name
jars = sorted(args.netlogo_app.glob('*.jar'))
assert jars
args.new_output.mkdir()
output = args.new_output.resolve()
for name in expected_assets:
    destination = output / name
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(args.runtime_assets / name, destination)
shutil.copy2(model, output / 'model.nlogo')
command = [args.java, '-Xmx1g', '-Djava.awt.headless=true', '-cp',
           str(output) + ':' + str(args.netlogo_app.resolve() / '*'), 'Replay',
           str(output / 'model.nlogo'), row['group_A'], row['group_B'], row['steps'],
           str(output / 'trajectory.csv')]
provenance = {'input': row, 'manifest_sha256': summary['manifest_sha256'],
              'assets_sha256': expected_assets,
              'runtime_jars_sha256': {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in jars},
              'timeout_seconds': args.timeout_seconds, 'maximum_output_bytes': 52428800,
              'command': command}
(output / 'provenance.json').write_text(json.dumps(provenance, indent=2) + '\n')
started = time.monotonic()
with (output / 'terminal.log').open('x') as log:
    result = subprocess.run(command, cwd=output, stdout=log, stderr=subprocess.STDOUT,
                            timeout=args.timeout_seconds)
receipt = {'exit_code': result.returncode, 'elapsed_seconds': time.monotonic() - started}
(output / 'terminal.json').write_text(json.dumps(receipt, indent=2) + '\n')
assert result.returncode == 0
assert sum(p.stat().st_size for p in output.rglob('*') if p.is_file()) < 52428800
with (output / 'trajectory.csv').open() as file:
    observations = list(csv.DictReader(file))
assert len(observations) == 20001
assert len(observations[0]) == 17
for tick, observation in enumerate(observations):
    assert float(observation['tick']) == tick
    assert all(math.isfinite(float(value)) for value in observation.values())
validation = {'run_id': args.run_id, 'observations': len(observations),
              'trajectory_sha256': hashlib.sha256((output / 'trajectory.csv').read_bytes()).hexdigest(),
              'scope': 'One complete frozen input; not an ensemble aggregate or paper replication.'}
(output / 'validation.json').write_text(json.dumps(validation, indent=2) + '\n')
print(json.dumps(validation))
