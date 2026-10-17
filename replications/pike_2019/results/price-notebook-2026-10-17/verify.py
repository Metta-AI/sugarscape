import csv
import json
import math
from collections import defaultdict
from pathlib import Path
import statistics
import sys
import numpy as np
base = Path('/Users/relh/Code/workspace/sugarscape-replication-evidence')
output = Path(sys.argv[1])
counts = defaultdict(lambda: defaultdict(int))
values = defaultdict(list)
windows = defaultdict(list)
for phase, directory in [(1, base/'pike-phase1-complete-001/reconciliation'), (3, base/'pike-phase3-complete-001/reconciled')]:
    report = json.loads((directory/'reconciliation.json').read_text())
    for i in range(len(report['segments'])):
        with (directory/f'segment-{i:02d}/price-measurements.csv').open() as stream:
            for row in csv.DictReader(stream):
                if phase == 1:
                    if row['variant'] != 'standard': continue
                    variant = 'standard'
                else:
                    if row['selector'] != 'released' or row['threshold'] != '10': continue
                    variant = row['approach']
                count = counts[variant]
                trades = int(row['trades'])
                count['steps'] += 1
                count['no_trade_steps'] += trades == 0
                count['omitted_single_trade_steps'] += trades == 1
                count['histogram_steps'] += trades >= 2
                count['scatter_transactions'] += trades if trades >= 2 else 0
                if trades >= 2: values[variant].append(float(row['sample_sd_log_price']))
                step = int(row['step'])
                if step <= 100 or step >= 901:
                    window = 'early' if step <= 100 else 'late'
                    if trades >= 2:
                        windows[variant, int(row['numpy_seed']), window].append(float(row['sample_sd_log_price']))
audit = json.loads((output/'audit.json').read_text())
for variant, expected in counts.items():
    for key, value in expected.items(): assert audit['counts'][variant][key] == value
rows = list(csv.DictReader((output/'run-measurements.csv').open()))
errors = []
for row in rows:
    if row['metric'] != 'sample_sd_log_price': continue
    source = windows[row['variant'], int(row['seed']), row['window']]
    assert int(row['defined_steps']) == len(source)
    if source:
        error = abs(float(row['mean_over_defined_steps']) - statistics.fmean(source))
        errors.append(error)
        assert error <= 1e-12
    else: assert row['mean_over_defined_steps'] == ''
hist = list(csv.DictReader((output/'histograms.csv').open()))
for variant, source in values.items():
    bins, edges = np.histogram(source, bins=500)
    actual = [row for row in hist if row['variant'] == variant]
    assert [int(row['count']) for row in actual] == bins.tolist()
    assert all(math.isclose(float(row['left']), edges[i], abs_tol=1e-12, rel_tol=1e-12) and math.isclose(float(row['right']), edges[i+1], abs_tol=1e-12, rel_tol=1e-12) for i,row in enumerate(actual))
result = {'price_step_records': sum(v['steps'] for v in counts.values()), 'count_fields': sum(len(v) for v in counts.values()), 'histogram_bins':len(hist), 'window_measurements':600, 'defined_window_measurements':len(errors), 'max_window_error':max(errors), 'scope':'Independent previously audited per-step CSVs reproduce all count fields, histogram bins and600 SD(log price) window records. No unit tests or new simulations.'}
Path(__file__).with_name('verification.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result))
