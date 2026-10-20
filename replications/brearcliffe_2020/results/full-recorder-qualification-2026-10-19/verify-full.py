import csv
import hashlib
import json
import math
import sys
from pathlib import Path

custom, native, output = map(Path, sys.argv[1:])
for name, expected in json.loads((custom / 'input-sha256.json').read_text()).items():
    assert hashlib.sha256((custom / name).read_bytes()).hexdigest() == expected, name
for root in (custom, native):
    assert json.loads((root / 'terminal.json').read_text())['exit_code'] == 0
with (custom / 'trajectory.csv').open() as f:
    recorded = list(csv.DictReader(f))
with (native / 'native-table.csv').open() as f:
    rows = list(csv.reader(f))
header_index = next(i for i, row in enumerate(rows) if row and row[0] == '[run number]')
reference = list(csv.DictReader((native / 'native-table.csv').read_text().splitlines()[header_index:]))
assert len(recorded) == len(reference) == 20001
fields = list(recorded[0])[1:]
assert fields == rows[header_index][10:]
matched = 0
for tick, (actual, expected) in enumerate(zip(recorded, reference)):
    assert float(actual['tick']) == float(expected['[step]']) == tick
    for field in fields:
        a, b = float(actual[field]), float(expected[field])
        assert math.isfinite(a) and math.isfinite(b)
        assert a == b, (tick, field, a, b)
        matched += 1
    for field in fields[:2]:
        value = float(actual[field])
        assert value.is_integer() and 0 < value <= 400
    for field in fields[8:12]:
        value = float(actual[field])
        assert value.is_integer() and value >= 0
        if tick:
            assert value >= float(recorded[tick - 1][field])
result = {
    'observations': len(recorded), 'compared_fields': matched,
    'exact_matches': matched, 'differences': [],
    'seed': 20261019, 'pairing': ['Rule M', 'EC'],
    'population_ranges': {field: [min(float(r[field]) for r in recorded), max(float(r[field]) for r in recorded)] for field in fields[:2]},
    'trajectory_sha256': hashlib.sha256((custom / 'trajectory.csv').read_bytes()).hexdigest(),
    'native_table_sha256': hashlib.sha256((native / 'native-table.csv').read_bytes()).hexdigest(),
    'scope': 'Full-horizon recorder qualification for one prospective seed and pairing; not paper replication or independent model validation.'
}
output.write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(result))
