from pathlib import Path
import gzip
import hashlib
import json
import math
import zipfile

root = Path(__file__).resolve().parent
manifest = json.loads((root / 'manifest.json').read_text())
archive = root.parent / 'papers/blueprints-runtimes.zip'
assert hashlib.sha256(archive.read_bytes()).hexdigest() == manifest['archive_sha256']
with zipfile.ZipFile(archive) as bundle:
    original = bundle.read(manifest['entry'])
assert (root / 'original.config').read_bytes() == original
assert hashlib.sha256(original).hexdigest() == manifest['original_config_sha256']
config = json.loads(original)
effective = json.loads((root / 'config.json').read_text())
assert hashlib.sha256((root / 'config.json').read_bytes()).hexdigest() == manifest['config_sha256']
config['logfile'] = str(root / 'trajectory.json')
assert effective == config
assert json.loads((root / 'exit.json').read_text())['exit_code'] == 0
pins = json.loads((root.parent.parent / 'sugarscape-blueprints/replications/blueprints_2024/source-sha256.json').read_text())
assert manifest['source_sha256'] == pins['source_sha256']
compressed = (root / 'trajectory.json.gz').read_bytes()
raw = gzip.decompress(compressed)
assert raw == (root / 'trajectory.json').read_bytes()
rows = json.loads(raw)
assert [row['timestep'] for row in rows] == list(range(len(rows)))
assert rows[0]['population'] == config['startingAgents'] == 250
arrays = {'agentWealths', 'agentTimesToLive', 'agentTimesToLiveAgeLimited'}
for row in rows:
    assert row['seed'] == config['seed'] and 0 <= row['population'] <= 2500
    assert {key for key, value in row.items() if isinstance(value, list)} == arrays
    assert all(math.isfinite(value) for key, value in row.items() if key not in arrays)
    assert all(math.isfinite(value) for key in arrays for value in row[key])
final = rows[-1]
assert final['timestep'] == config['timesteps'] or final['population'] == 0
report = {'entry': manifest['entry'], 'source_files_verified': len(pins['source_sha256']),
          'observations': len(rows), 'final_timestep': final['timestep'], 'final_population': final['population'],
          'trajectory_sha256': hashlib.sha256(raw).hexdigest(), 'compressed_sha256': hashlib.sha256(compressed).hexdigest(),
          'scope': 'One full deposited runtime-archive condition. Original input changed only logfile. Not wholearchive or Table6 completion.'}
(root / 'audit.json').write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps(report))
