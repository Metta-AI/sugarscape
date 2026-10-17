import csv
import json
from pathlib import Path
import sys
import numpy as np

base = Path('/Users/relh/Code/workspace/sugarscape-replication-evidence')
analysis = Path(sys.argv[1])
actual = {}
for r in csv.DictReader((analysis/'run-measurements.csv').open()):
    key = (r['condition'], int(r['seed']), r['window'], r['metric'])
    assert key not in actual
    actual[key] = r
errors = []
for phase, directory in [(1,base/'pike-phase1-complete-001/reconciliation'), (2,base/'pike-phase2-complete-001/reconciled'), (3,base/'pike-phase3-complete-001/reconciled')]:
    report = json.loads((directory/'reconciliation.json').read_text())
    for r in report['runs']:
        condition = 'phase1-'+r['variant'] if phase == 1 else f"{r['approach']}-{r['threshold']}-{r['selector'] if phase == 3 else 'none'}"
        for window in ['early','late']:
            expected = r['windows'][window]['sample_sd_log_price']
            value = actual[condition,r['numpy_seed'],window,'sample_sd_log_price']
            assert int(value['defined_steps']) == expected['defined_steps']
            if expected['defined_steps']:
                errors.append(abs(float(value['mean'])-expected['mean_over_defined_steps']))
            else: assert value['mean']==''
    window_prices = {}
    for i in range(len(report['segments'])):
        with (directory/f'segment-{i:02d}/price-measurements.csv').open() as stream:
            for r in csv.DictReader(stream):
                step = int(r['step'])
                if not(step<=100 or step>=901): continue
                condition = 'phase1-'+r['variant'] if phase == 1 else f"{r['approach']}-{r['threshold']}-{r['selector'] if phase == 3 else 'none'}"
                key=(condition,int(r['numpy_seed']),'early' if step<=100 else 'late','abs_log_geometric_mean')
                if key not in window_prices: window_prices[key]=[]
                if r['geometric_mean_price']: window_prices[key].append(float(r['geometric_mean_price']))
    for key, prices in window_prices.items():
        value=actual[key]
        assert int(value['defined_steps'])==len(prices)
        if prices: errors.append(abs(float(value['mean'])-float(np.abs(np.log(prices)).mean())))
        else: assert value['mean']==''
assert len(actual)==8400 and max(errors)<1e-12
result={'measurements':len(actual),'defined_measurements':len(errors),'max_error':max(errors),'scope':'4200 dispersion windows checked against original raw-reconciliation summaries;4200 absolute-log price windows independently calculated with NumPy from audited step prices. Missing counts retained.'}
Path(__file__).with_name('measurements.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result))
