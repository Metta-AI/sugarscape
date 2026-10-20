"""Recompute all terminal native recorder comparisons from retained trajectories."""

import argparse
import csv
import hashlib
import json
import math
from pathlib import Path

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('retained_run', type=Path)
parser.add_argument('new_report', type=Path)
args = parser.parse_args()
root = args.retained_run
plan = json.loads((root / 'plan.json').read_text())
terminal = json.loads((root / 'terminal.json').read_text())
assert terminal['exit_code'] == 0
assert terminal['completed_pairings'] == len(plan['pairings'])
for name, digest in json.loads((root / 'input-sha256.json').read_text()).items():
    assert hashlib.sha256((root / name).read_bytes()).hexdigest() == digest, name
commands = json.loads((root / 'commands.json').read_text())
assert [r['pairing'] for r in commands] == plan['pairings']
comparisons = []
for entry in commands:
    directory = root / Path(entry['directory']).name
    for kind in ('custom', 'native'):
        assert json.loads((directory / f'{kind}-terminal.json').read_text())['exit_code'] == 0
    with (directory / 'trajectory.csv').open() as file:
        custom = list(csv.DictReader(file))
    lines = (directory / 'native-table.csv').read_text().splitlines()
    start = next(i for i, row in enumerate(csv.reader(lines)) if row and row[0] == '[run number]')
    reference = list(csv.DictReader(lines[start:]))
    fields = list(custom[0])[1:]
    assert len(fields) == 16
    assert fields == list(reference[0])[10:]
    assert len(custom) == len(reference) == plan['steps'] + 1
    for tick, (a, b) in enumerate(zip(custom, reference)):
        assert float(a['tick']) == float(b['[step]']) == tick
        for field in fields:
            left, right = float(a[field]), float(b[field])
            assert math.isfinite(left) and math.isfinite(right)
            assert left == right, (entry['pairing'], tick, field, left, right)
    result = {'pairing': entry['pairing'], 'observations': len(custom),
              'compared_fields': len(custom) * 16, 'differences': [],
              'trajectory_sha256': hashlib.sha256((directory / 'trajectory.csv').read_bytes()).hexdigest(),
              'native_table_sha256': hashlib.sha256((directory / 'native-table.csv').read_bytes()).hexdigest()}
    assert result == json.loads((directory / 'comparison.json').read_text())
    comparisons.append(result)
report = {'pairings_verified': len(comparisons),
          'compared_fields': sum(c['compared_fields'] for c in comparisons),
          'all_exact': True, 'comparisons': comparisons,
          'scope': 'Native recorder qualification, not independent-model or paper replication.'}
with args.new_report.open('x') as file:
    file.write(json.dumps(report, indent=2) + '\n')
print(json.dumps({k: v for k, v in report.items() if k != 'comparisons'}))
