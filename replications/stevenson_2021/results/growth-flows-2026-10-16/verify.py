import csv
import hashlib
import json
from pathlib import Path
import numpy as np

root = Path('/Users/relh/Code/workspace/sugarscape-replication-evidence')
run = root / 'stevenson-2021-growth-001'
out = root / 'stevenson-growth-flows-001'
expected = list(csv.DictReader((out / 'seed-bands.csv').open()))
checked = 0
for scenario in ('low-fertility', 'birth-cost'):
    for seed in range(1, 101):
        values = np.genfromtxt(run / f'{scenario}-{seed}.csv', delimiter=',', names=True, dtype=np.int64)
        before = np.concatenate(([1], values['population'][:-1]))
        labels = np.digitize(before, [11, 101, 401, 701])
        rows = [r for r in expected if r['scenario'] == scenario and int(r['seed']) == seed]
        for label, row in enumerate(rows):
            mask = labels == label
            actual = [mask.sum(), before[mask].sum(), values['births'][mask].sum(), values['deaths'][mask].sum()]
            assert actual == [int(row[k]) for k in ('cycles', 'agent_cycles', 'births', 'deaths')]
            checked += 1
report = {'seed_band_rows_exact': checked, 'observations': 600000, 'method': 'Independent NumPy digitize and masked sums over original CSV trajectories', 'seed_bands_sha256': hashlib.sha256((out / 'seed-bands.csv').read_bytes()).hexdigest()}
(out / 'independent-validation.json').write_text(json.dumps(report, indent=2) + '\n')
print(report)
