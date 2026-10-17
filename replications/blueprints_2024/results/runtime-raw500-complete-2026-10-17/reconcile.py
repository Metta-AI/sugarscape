from pathlib import Path
import gzip
import hashlib
import json
import zipfile
from collections import Counter

root = Path(__file__).resolve().parent
base = root.parent
report = json.loads((root / 'audit.json').read_text())
assert report['complete_batch'] and report['validated_runs'] == 99
pilot = base / 'blueprints-runtime-pilot-001'
pilot_report = json.loads((pilot / 'audit.json').read_text())
raw = gzip.decompress((pilot / 'trajectory.json.gz').read_bytes())
assert hashlib.sha256(raw).hexdigest() == pilot_report['trajectory_sha256']
rows = json.loads(raw)
assert len(rows) == pilot_report['observations'] == 501
assert rows[-1]['timestep'] == 500 and rows[-1]['population'] == pilot_report['final_population'] == 431
with zipfile.ZipFile(base / 'papers/blueprints-runtimes.zip') as archive:
    entries = sorted(name for name in archive.namelist() if name.startswith('500-rawSugarscape'))
    assert archive.read(pilot_report['entry']) == (pilot / 'original.config').read_bytes()
assert [pilot_report['entry'], *[row['entry'] for row in report['results']]] == entries
seeds = [json.loads((pilot / 'original.config').read_text())['seed'], *[row['seed'] for row in report['results']]]
assert len(seeds) == len(set(seeds)) == 100
counts = Counter(report['counts'])
counts['better_or_equal'] += 1
result = {'complete_archived_raw500_group': True, 'unique_inputs': 100, 'required_group_inputs': 100,
          'unique_seeds': 100, 'observations': report['observations'] + pilot_report['observations'],
          'counts_native_plot_rule': dict(counts), 'population_equal_250': sum(row['final_population'] == 250 for row in report['results']),
          'full_runtime_archive_inputs': 1200, 'producer_exit_code': json.loads((base / 'blueprints-runtime-raw500-remaining-001/job-exit.json').read_text())['exit_code'],
          'scope': 'All100deposited raw-model500step configurations, pilot counted once. Disjoint from homogeneous500seeds. No direct equality test against Table6 based on claimed500seeds.'}
assert result['producer_exit_code'] == 0
(root / 'reconciliation.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(result))
