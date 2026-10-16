"""Describe published Figure 1 against all 100 audited seeds of one scenario."""
import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('run', type=Path)
parser.add_argument('audit', type=Path)
parser.add_argument('scenario', choices=['low-fertility', 'birth-cost'])
parser.add_argument('output', type=Path)
args = parser.parse_args()
root = Path(__file__).resolve().parent
audit = json.loads((args.audit / 'audit.json').read_text())
assert audit['manifest_sha256'] == hashlib.sha256((args.run / 'manifest.json').read_bytes()).hexdigest()
ledger = (args.audit / 'ledger-snapshot.jsonl').read_bytes()
assert hashlib.sha256(ledger).hexdigest() == audit['ledger_snapshot_sha256']
records = [json.loads(line) for line in ledger.splitlines()]
records = [row for row in records if row['scenario'] == args.scenario]
assert [row['seed'] for row in records] == list(range(1, 101)), 'Require all 100 declared scenario seeds'
cycles = np.arange(100, 50000, 100)
samples = {name: [] for name in ['population', 'mean_age', 'gini', 'elite_age']}
for record in records:
    stem = f"{args.scenario}-{record['seed']}"
    for name in [stem + '.csv', stem + '-observations.csv']:
        assert hashlib.sha256((args.run / name).read_bytes()).hexdigest() == record['raw_sha256'][name]
    aggregate = pd.read_csv(args.run / (stem + '.csv')).set_index('cycle')
    observations = pd.read_csv(args.run / (stem + '-observations.csv'))
    elite = observations[observations.kind == 'elite'].set_index('cycle')
    for metric in samples:
        frame, column = (elite, 'mean_age') if metric == 'elite_age' else (aggregate, metric)
        samples[metric].append(frame.loc[cycles, column].to_numpy())
figure = root / 'results/figure1-vector-2026-10-16'
extraction = json.loads((figure / 'extraction.json').read_text())
summaries, tables = [], []
for metric, runs in samples.items():
    series = metric + '_' + args.scenario.replace('-', '_')
    source = figure / (series + '.csv.gz')
    provenance = next(row for row in extraction['curves'] if row['series'] == series)
    assert hashlib.sha256(source.read_bytes()).hexdigest() == provenance['csv_gzip_sha256']
    vertices = pd.read_csv(source)
    # Exported path boundaries repeat vertices; averaging is only over identical-time coordinates.
    curve = vertices.groupby('approximate_cycle', sort=True).approximate_value.mean()
    assert curve.index.min() <= cycles.min() and curve.index.max() >= cycles.max()
    published = np.interp(cycles, curve.index, curve.to_numpy())
    matrix = np.asarray(runs)
    assert matrix.shape == (100, 499) and np.isfinite(matrix).all()
    low, median, high = np.quantile(matrix, [.025, .5, .975], axis=0)
    late = cycles > 35000
    seed_means = matrix[:, late].mean(axis=1)
    summaries.append({'metric': metric, 'shared_cycles': len(cycles),
        'published_fraction_inside_pointwise_seed_95_percent_interval': float(((published >= low) & (published <= high)).mean()),
        'median_curve_mean_absolute_difference': float(np.abs(published - median).mean()),
        'late_shared_cycle_published_mean': float(published[late].mean()),
        'late_seed_mean_average': float(seed_means.mean()),
        'late_seed_mean_quantiles_025_50_975': np.quantile(seed_means, [.025, .5, .975]).tolist(),
        'source_csv_gzip_sha256': provenance['csv_gzip_sha256']})
    tables.append(pd.DataFrame({'metric': metric, 'cycle': cycles, 'published_approximate': published,
        'seed_q025': low, 'seed_median': median, 'seed_q975': high}))
report = {'scenario': args.scenario, 'seeds': list(range(1, 101)), 'metrics': summaries,
    'audit_sha256': hashlib.sha256((args.audit / 'audit.json').read_bytes()).hexdigest(),
    'comparison_source_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    'limits': 'Descriptive comparison, not a replication verdict or hypothesis test. Pointwise seed intervals are not confidence intervals or simultaneous bands. Published seed and aggregation are unknown. Vector coordinates are approximate. Common samples exclude cycle 50000 because some published curves end slightly earlier. Late discrete samples differ from the extraction report segment integral.'}
args.output.mkdir(parents=True, exist_ok=False)
pd.concat(tables).to_csv(args.output / 'comparison.csv', index=False)
(args.output / 'comparison.json').write_text(json.dumps(report, indent=2, allow_nan=False) + '\n')
print(json.dumps(summaries, indent=2))
