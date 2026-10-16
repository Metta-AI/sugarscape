"""Replay a completed 2003 run with passive native seed accounting and exact trajectory parity."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('baseline', type=Path)
parser.add_argument('output', type=Path)
args = parser.parse_args()
baseline = args.baseline.resolve()
provenance = json.loads((baseline / 'provenance.json').read_text())
audit = json.loads((baseline / 'audit.json').read_text())
assert provenance['study'] == 'Buzing2003' and provenance['cycles'] == 500
assert json.loads((baseline / 'exit.json').read_text()) == {'exit_code': 0}
for filename, checksum in provenance['source_sha256'].items():
    assert hashlib.sha256(Path(filename).read_bytes()).hexdigest() == checksum
for filename, checksum in provenance['configuration_sha256'].items():
    assert hashlib.sha256((baseline / filename).read_bytes()).hexdigest() == checksum
output = args.output.resolve()
output.mkdir(parents=True, exist_ok=False)
shutil.copytree(baseline / 'config', output / 'config')
sources = [Path(p) for p in provenance['source_sha256']]
original = next(p for p in sources if p.name == 'Scape.java')
raw = original.read_bytes()
marker = b'    public void sendDataToDB()\n    {'
assert raw.count(marker) == 1
modified = output / 'Scape.java'
modified.write_bytes(raw.replace(marker, marker + b'\n        ResourceAudit.observe((SugarScape) this);'))
sources[sources.index(original)] = modified
observer = output / 'ResourceAudit.java'
shutil.copy2(Path(__file__).with_name('ResourceAudit.java'), observer)
sources.append(observer)
command = list(provenance['command'])
assert hashlib.sha256(Path(command[-1]).read_bytes()).hexdigest() == provenance['reference_manifest']['adapter_sha256']
java = Path(command[0])
classpath_index = command.index('-cp') + 1
_, library = command[classpath_index].split(':', 1)
classes = output / 'classes'
classes.mkdir()
with (output / 'compile.log').open('w') as log:
    subprocess.run([str(java.with_name('javac')), '-encoding', 'ISO-8859-1', '-cp', library, '-d', str(classes), *map(str, sources)], stdout=log, stderr=subprocess.STDOUT, check=True)
command[classpath_index] = f'{classes}:{library}'
with (output / 'run.log').open('w') as log:
    result = subprocess.run(command, cwd=output, stdout=log, stderr=subprocess.STDOUT, timeout=120)
(output / 'exit.json').write_text(json.dumps({'exit_code': result.returncode}) + '\n')
assert result.returncode == 0
log = (output / 'run.log').read_text()
assert f"iterations=500,initial=400,final={audit['final_population']}" in log
rows = [list(map(float, s.split(',')[1:])) for s in log.splitlines() if s.startswith('resource-audit,')]
assert len(rows) == 500 and [r[0] for r in rows] == list(range(500))
assert all(len(r) == 6 and r[1] == 500 and 0 <= r[3] <= r[4] <= 1250 for r in rows)
assert len(audit['output_sha256']) == 10
for filename, checksum in audit['output_sha256'].items():
    data = (output / 'data' / filename).read_bytes()
    assert data == (baseline / 'data' / filename).read_bytes()
    assert hashlib.sha256(data).hexdigest() == checksum
report = {'baseline': str(baseline), 'observed_cycles': 500, 'matching_native_files': 10,
          'seed_count': 500, 'each_maximum_size_count': 125, 'growth_rate': 3,
          'available_sugar_min_max': [min(r[3] for r in rows), max(r[3] for r in rows)],
          'maximum_seeds_awaiting_redistribution': max(r[2] for r in rows),
          'source_sha256': {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in sources},
          'configuration_sha256': provenance['configuration_sha256'],
          'baseline_provenance_sha256': hashlib.sha256((baseline / 'provenance.json').read_bytes()).hexdigest(),
          'output_sha256': audit['output_sha256'], 'command': command,
          'scope': 'End-of-cycle seed conservation and plant accounting, with exact observer parity. Does not prove intermediate-stage accounting or historical dynamics.'}
(output / 'audit.json').write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps({k:v for k,v in report.items() if k not in ('source_sha256', 'output_sha256', 'command')}))
