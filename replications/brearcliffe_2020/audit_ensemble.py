"""Audit complete frozen inputs and emit only disjoint remaining ensemble work."""

import argparse
import csv
import hashlib
import json
import math
from pathlib import Path

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('prepared', type=Path)
parser.add_argument('new_output', type=Path)
parser.add_argument('completed_runs', type=Path, nargs='+')
args = parser.parse_args()
manifest = args.prepared / 'manifest.csv'
manifest_hash = hashlib.sha256(manifest.read_bytes()).hexdigest()
assert manifest_hash == json.loads((args.prepared / 'summary.json').read_text())['manifest_sha256']
with manifest.open() as file:
    rows = list(csv.DictReader(file))
expected = {row['run_id']: row for row in rows}
assert len(expected) == len(rows) == 1600
completed = {}
for root in args.completed_runs:
    provenance = json.loads((root / 'provenance.json').read_text())
    validation = json.loads((root / 'validation.json').read_text())
    terminal = json.loads((root / 'terminal.json').read_text())
    row = provenance['input']
    run_id = row['run_id']
    assert run_id not in completed, f'Duplicate completed input: {run_id}'
    assert row == expected[run_id]
    assert provenance['manifest_sha256'] == manifest_hash
    assert terminal['exit_code'] == 0
    assert validation['run_id'] == run_id
    assert validation['observations'] == 20001
    assert hashlib.sha256((root / 'model.nlogo').read_bytes()).hexdigest() == row['model_sha256']
    for name, digest in provenance['assets_sha256'].items():
        assert hashlib.sha256((root / name).read_bytes()).hexdigest() == digest, name
    trajectory = root / 'trajectory.csv'
    digest = hashlib.sha256(trajectory.read_bytes()).hexdigest()
    assert digest == validation['trajectory_sha256']
    with trajectory.open() as file:
        observations = list(csv.DictReader(file))
    assert len(observations) == 20001
    fields = ['tick', 'count group-A', 'count group-B', 'mean [sugar] of group-A',
              'mean [sugar] of group-B', 'mean [vision] of group-A', 'mean [vision] of group-B',
              'mean [metabolism] of group-A', 'mean [metabolism] of group-B',
              'combat-agent-a-die', 'combat-agent-b-die', 'starve-agent-a-die', 'starve-agent-b-die',
              'mean [age] of group-A', 'mean [age] of group-B', 'max [age] of group-A', 'max [age] of group-B']
    assert list(observations[0]) == fields
    previous_deaths = [0.0] * 4
    for tick, observation in enumerate(observations):
        values = [float(observation[field]) for field in fields]
        assert all(math.isfinite(value) for value in values)
        assert values[0] == tick
        assert all(value.is_integer() and 0 < value <= 400 for value in values[1:3])
        assert all(value > 0 for value in values[3:5])
        assert all(1 <= value <= 6 for value in values[5:7])
        assert all(1 <= value <= 4 for value in values[7:9])
        deaths = values[9:13]
        assert all(value.is_integer() and value >= old for value, old in zip(deaths, previous_deaths))
        previous_deaths = deaths
        assert all(0 <= values[13 + i] <= values[15 + i] <= tick for i in range(2))
        if tick == 0:
            assert values[1:3] == [400, 400] and deaths == [0, 0, 0, 0]
    completed[run_id] = {'run_id': run_id, 'directory': str(root.resolve()),
                         'trajectory_sha256': digest, 'observations': len(observations),
                         'elapsed_seconds': terminal['elapsed_seconds']}
remaining = [row for row in rows if row['run_id'] not in completed]
assert len(remaining) + len(completed) == 1600
report = {'manifest_sha256': manifest_hash, 'completed_inputs': len(completed),
          'remaining_inputs': len(remaining), 'observations': sum(r['observations'] for r in completed.values()),
          'completed': list(completed.values()),
          'scope': 'Verified complete inputs only; no full-ensemble or published-result verdict.'}
args.new_output.mkdir()
(args.new_output / 'audit.json').write_text(json.dumps(report, indent=2) + '\n')
with (args.new_output / 'remaining.csv').open('x', newline='') as file:
    writer = csv.DictWriter(file, fieldnames=list(rows[0]))
    writer.writeheader()
    writer.writerows(remaining)
print(json.dumps({k: v for k, v in report.items() if k != 'completed'}))
