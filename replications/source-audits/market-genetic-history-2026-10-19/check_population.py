"""Audit released historical tables without treating them as fresh simulation results."""
from pathlib import Path
import hashlib
import json
import math
import struct
import sys
import pyarrow
import pyarrow.parquet as pq

root, output = map(Path, sys.argv[1:])
assert not output.exists()
reports = []
for breed in ('basic', 'optimizer'):
    path = root / (breed + '-population_df')
    table = pq.read_table(path).to_pydict()
    runs = [str(i) for i in range(30)]
    assert list(table) == runs + ['mean', '__index_level_0__']
    assert table['__index_level_0__'] == list(range(5000))
    assert all(len(values) == 5000 for values in table.values())
    assert all(math.isfinite(v) and v >= 0 and int(v) == v for key in runs for v in table[key])
    assert all(table[key][0] == 2000 for key in runs)
    individual = pq.read_table(root / (breed + '-0.parquet')).to_pydict()
    assert individual['population'] == table['0']
    errors = [abs(math.fsum(table[key][t] for key in runs) / 30 - table['mean'][t]) for t in range(5000)]
    assert str(pq.read_table(path).schema.field('mean').type) == 'float'
    rounded = [struct.unpack('f', struct.pack('f', math.fsum(table[key][t] for key in runs) / 30))[0] for t in range(5000)]
    assert rounded == table['mean']
    reports.append({'breed': breed, 'run_columns': 30, 'observations_per_run': 5000, 'finite_population_values': 150000, 'run_zero_exact': True, 'maximum_mean_error': max(errors), 'table_sha256': hashlib.sha256(path.read_bytes()).hexdigest()})
result = {'pyarrow_version': pyarrow.__version__, 'tables': reports, 'scope': 'Historical deposited outputs:30 runs of5000 observations, not the paper100 replicates/60000–100000 periods. Independent arithmetic validates saved tables only; no new simulation or completed-study credit.'}
output.write_text(json.dumps(result, indent=2)+'\n')
print(json.dumps(result))
