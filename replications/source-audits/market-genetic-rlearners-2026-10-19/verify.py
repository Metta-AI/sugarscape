"""Validate pinned author artifacts and the deposited population traces."""
from pathlib import Path
import hashlib
import json
import math
import sys
import pyarrow.parquet as pq
root, output = map(Path, sys.argv[1:])
assert not output.exists()
manifest = json.loads((root / 'source-manifest.json').read_text())
for row in manifest:
    raw = (root / 'source' / row['path']).read_bytes()
    assert len(raw) == row['bytes']
    assert hashlib.sha256(raw).hexdigest() == row['sha256']
    assert hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest() == row['git_blob']
assert (root / 'source/LICENSE').read_text().startswith('MIT License\n\nCopyright (c) 2024 Zach Johnson')
records = json.loads((root / 'population-inspection.json').read_text())
assert len(records) == 8
assert {Path(r['path']).stem for r in records} == {'0','1','3','4','5','6','8','9'}
for row in records:
    p = root / 'population' / Path(row['path']).name
    raw = p.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == row['sha256']
    assert hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest() == row['git_blob']
    table = pq.read_table(p)
    assert table.column_names == ['population'] and table.num_rows == 10000
    values = table.column('population').to_pylist()
    assert values[0] == 200
    assert all(math.isfinite(v) and v >= 0 and int(v) == v for v in values)
for item in json.loads((root / 'driver-comparison.json').read_text()):
    raw = (root / 'history' / (item['revision'] + '-GUI.py')).read_bytes()
    assert hashlib.sha256(raw).hexdigest() == item['sha256']
    assert hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest() == item['git_blob']
    lines = raw.decode().splitlines()
    assert all(lines[r['line']-1].strip() == r['text'] for r in item['protocol_lines'])
report = {'source_files_verified': len(manifest), 'driver_revisions_verified': 4, 'deposited_population_runs': 8, 'population_observations_checked': 80000, 'initial_population': 200, 'observations_per_run': 10000, 'scope': 'Deposited artifact inspection only. Different protocol from Market Algorithm paper; no simulation or completed-study credit.'}
output.write_text(json.dumps(report, indent=2)+'\n')
print(json.dumps(report))
