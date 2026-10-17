from pathlib import Path
import collections
import csv
import hashlib
import json
import math
import statistics
import numpy as np

root = Path(__file__).resolve().parent
notebook = root.parent.parent / 'sugarscape-pike-initial-reference/Analysis Code/Data Analysis-Initial.ipynb'
raw = notebook.read_bytes()
assert hashlib.sha256(raw).hexdigest() == '4dff915e0804daf58da435db05ed8d8027423e024a737d13f9642b5fc5298e8f'
source = ''.join(json.loads(raw)['cells'][2]['source'])
namespace = {'stdev': statistics.stdev, 'log': math.log}
exec(compile(source, str(notebook), 'exec'), namespace)
reconciliation = json.loads((root.parent / 'pike-phase1-complete-001/reconciliation/reconciliation.json').read_text())
prices = collections.defaultdict(dict)
for segment in reconciliation['segments']:
    run = Path(segment['run'])
    for line in (run / 'completed.jsonl').read_text().splitlines():
        record = json.loads(line)
        variant, seed = record['variant'], record['numpy_seed']
        data = (run / f'{variant}-{seed}/prices.json').read_bytes()
        assert hashlib.sha256(data).hexdigest() == record['hashes']['prices.json']
        assert seed not in prices[variant]
        prices[variant][seed] = json.loads(data)
with (root / 'dispersion-histograms.csv').open() as stream:
    histograms = list(csv.DictReader(stream))
counts = {}
for variant, runs in prices.items():
    assert sorted(runs) == list(range(100))
    values = namespace['make_distro'](runs)
    counts[variant] = len(values)
    actual, edges = np.histogram(values, bins=500)
    expected = [row for row in histograms if row['variant'] == variant]
    assert [int(row['count']) for row in expected] == actual.tolist()
    assert [float(row['bin_left']) for row in expected] == edges[:-1].tolist()
    assert [float(row['bin_right']) for row in expected] == edges[1:].tolist()
assert not (root.parent / 'pike-phase1-analysis-incomplete-rejected-001').exists()
(root / 'notebook-verification.json').write_text(json.dumps({'notebook_sha256': hashlib.sha256(raw).hexdigest(),
 'cell_index': 2, 'native_price_files': 300, 'histogram_bins_exact': 1500, 'defined_dispersion_steps': counts,
 'incomplete_grid_rejected_before_output': True}, indent=2) + '\n')
print(counts)
