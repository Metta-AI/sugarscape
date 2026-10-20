"""Summarize exactly fifty audited full-length runs of one frozen method pairing."""

import argparse
from array import array
import csv
import gzip
import hashlib
import json
import math
from pathlib import Path
import random

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('prepared', type=Path)
parser.add_argument('audit_json', type=Path)
parser.add_argument('new_output', type=Path)
parser.add_argument('--interpretation', choices=['released-code', 'paper-table'], required=True)
parser.add_argument('--pair-index', type=int, choices=range(16), required=True)
args = parser.parse_args()
manifest = args.prepared / 'manifest.csv'
manifest_hash = hashlib.sha256(manifest.read_bytes()).hexdigest()
assert manifest_hash == json.loads((args.prepared / 'summary.json').read_text())['manifest_sha256']
with manifest.open() as file:
    selected = [row for row in csv.DictReader(file) if row['interpretation'] == args.interpretation
                and int(row['pair_index']) == args.pair_index]
selected.sort(key=lambda row: int(row['repetition']))
assert [int(row['repetition']) for row in selected] == list(range(50))
audit = json.loads(args.audit_json.read_text())
assert audit['manifest_sha256'] == manifest_hash
completed = {row['run_id']: row for row in audit['completed']}
assert len(completed) == len(audit['completed'])
missing = [row['run_id'] for row in selected if row['run_id'] not in completed]
assert not missing, f'Incomplete fifty-run cohort: {len(missing)} inputs missing.'
means = array('d', [0.0]) * (20001 * 16)
m2 = array('d', [0.0]) * (20001 * 16)
endpoints = []
source_hashes = {}
fields = ['count group-A', 'count group-B', 'mean [sugar] of group-A', 'mean [sugar] of group-B',
          'mean [vision] of group-A', 'mean [vision] of group-B', 'mean [metabolism] of group-A',
          'mean [metabolism] of group-B', 'combat-agent-a-die', 'combat-agent-b-die',
          'starve-agent-a-die', 'starve-agent-b-die', 'mean [age] of group-A', 'mean [age] of group-B',
          'max [age] of group-A', 'max [age] of group-B']
for count, row in enumerate(selected, 1):
    item = completed[row['run_id']]
    root = Path(item['directory'])
    assert item['observations'] == 20001
    provenance = json.loads((root / 'provenance.json').read_text())
    assert provenance['input'] == row and provenance['manifest_sha256'] == manifest_hash
    assert json.loads((root / 'terminal.json').read_text())['exit_code'] == 0
    assert hashlib.sha256((root / 'model.nlogo').read_bytes()).hexdigest() == row['model_sha256']
    trajectory = root / 'trajectory.csv'
    digest = hashlib.sha256(trajectory.read_bytes()).hexdigest()
    assert digest == item['trajectory_sha256']
    source_hashes[row['run_id']] = digest
    with trajectory.open() as file:
        reader = csv.DictReader(file)
        assert reader.fieldnames == ['tick', *fields]
        observations = 0
        for tick, observation in enumerate(reader):
            assert float(observation['tick']) == tick and tick <= 20000
            values = [float(observation[field]) for field in fields]
            assert all(math.isfinite(value) for value in values)
            for column, value in enumerate(values):
                index = tick * 16 + column
                difference = value - means[index]
                means[index] += difference / count
                m2[index] += difference * (value - means[index])
            observations += 1
        assert observations == 20001
        endpoints.append(values[2:])
# Resample entire runs, keeping the fourteen endpoint metrics paired.
rng = random.Random(20261019)
bootstrap = [[] for _ in range(14)]
bootstrap_indices = array('B')
for _ in range(20000):
    indices = [rng.randrange(50) for _ in range(50)]
    bootstrap_indices.extend(indices)
    for column in range(14):
        bootstrap[column].append(math.fsum(endpoints[i][column] for i in indices) / 50)
intervals = []
for column, samples in enumerate(bootstrap):
    samples.sort()
    bounds = []
    for probability in (0.025, 0.975):
        position = (len(samples) - 1) * probability
        lower = math.floor(position)
        bounds.append(samples[lower] + (position - lower) * (samples[lower + 1] - samples[lower]))
    intervals.append({'metric': fields[column + 2], 'mean': means[20000 * 16 + column + 2],
                      'sample_sd': math.sqrt(m2[20000 * 16 + column + 2] / 49),
                      'pointwise_percentile_interval_95': bounds})
args.new_output.mkdir()
(args.new_output / 'bootstrap-indices.u8.gz').write_bytes(gzip.compress(bootstrap_indices.tobytes(), mtime=0))
for name, values in [('means.csv', means), ('sample-sd.csv', array('d', (math.sqrt(v / 49) for v in m2)))]:
    with (args.new_output / name).open('x', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['tick', *fields])
        for tick in range(20001):
            writer.writerow([tick, *values[tick * 16:(tick + 1) * 16]])
report = {'interpretation': args.interpretation, 'pair_index': args.pair_index,
          'group_A': selected[0]['group_A'], 'group_B': selected[0]['group_B'], 'runs': 50,
          'observations': 1000050, 'manifest_sha256': manifest_hash,
          'audit_sha256': hashlib.sha256(args.audit_json.read_bytes()).hexdigest(),
          'trajectory_sha256': source_hashes, 'endpoint_statistics': intervals,
          'bootstrap': {'seed': 20261019, 'repetitions': 20000, 'unit': 'whole run',
                        'indices_sha256': hashlib.sha256(bootstrap_indices.tobytes()).hexdigest(),
                        'indices_format': '20000 rows of 50 zero-based uint8 run indices, row-major',
                        'quantile': 'linear interpolation, type7', 'coverage': 'pointwise, not simultaneous'},
          'scope': 'Arithmetic run means before logarithmic plotting; no published-result verdict from summary alone.'}
(args.new_output / 'summary.json').write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps({'runs': 50, 'observations': 1000050, 'pair_index': args.pair_index}))
