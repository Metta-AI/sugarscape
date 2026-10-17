"""Compute declared phase-one comparisons from a complete audited reconciliation."""
import argparse
import csv
import hashlib
import itertools
import json
import math
from pathlib import Path
import statistics

import numpy as np
from scipy import stats


def mean_interval(values):
    mean = statistics.fmean(values)
    half_width = float(stats.t.ppf(0.975, len(values) - 1)) * statistics.stdev(values) / math.sqrt(len(values))
    return {'n': len(values), 'mean': mean, 'sample_sd': statistics.stdev(values),
            'mean_ci95': [mean - half_width, mean + half_width]}


parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('reconciliation', type=Path)
parser.add_argument('output', type=Path)
args = parser.parse_args()
raw = (args.reconciliation / 'reconciliation.json').read_bytes()
report = json.loads(raw)
assert report['phase'] == 1 and report['complete_grid']
assert report['validated_runs'] == report['required_runs'] == 300
assert report['missing_ordinals'] == []
assert [row['ordinal'] for row in report['runs']] == list(range(300))
variants = ['standard', 'explicit', 'network']
targets = {'standard': 46.18, 'explicit': 46.96, 'network': 46.68}
values = {}
rows_by_variant = {}
for variant in variants:
    selected = [row for row in report['runs'] if row['variant'] == variant]
    assert [row['numpy_seed'] for row in selected] == list(range(100))
    rows_by_variant[variant] = selected
    values[variant] = [row['final_individual_agents'] for row in selected]
survivors = {variant: {**mean_interval(values[variant]), 'cached_author_mean': targets[variant],
                      'difference_from_cached_mean': statistics.fmean(values[variant]) - targets[variant]}
             for variant in variants}
comparisons = []
for left, right in itertools.combinations(variants, 2):
    test = stats.ttest_ind(values[left], values[right], equal_var=True)
    differences = [a - b for a, b in zip(values[left], values[right], strict=True)]
    comparisons.append({'left': left, 'right': right, 'paired_left_minus_right': mean_interval(differences),
                        'equal_variance_t': float(test.statistic), 'correct_two_sided_p': float(test.pvalue),
                        'historical_doubled_p': 2 * float(test.pvalue)})
measurements = {variant: [] for variant in variants}
input_hashes = {}
for index, segment in enumerate(report['segments']):
    directory = args.reconciliation / f'segment-{index:02d}'
    assert hashlib.sha256((directory / 'audit.json').read_bytes()).hexdigest() == segment['audit_sha256']
    path = directory / 'price-measurements.csv'
    input_hashes[str(path)] = hashlib.sha256(path.read_bytes()).hexdigest()
    with path.open() as stream:
        for row in csv.DictReader(stream):
            measurements[row['variant']].append(row)
prices = {}
histograms = []
for variant in variants:
    rows = measurements[variant]
    assert len(rows) == 100000
    assert {(int(row['numpy_seed']), int(row['step'])) for row in rows} == set(itertools.product(range(100), range(1, 1001)))
    dispersion = [float(row['sample_sd_log_price']) for row in rows if row['sample_sd_log_price'] != '']
    assert len(rows) - len(dispersion) == sum(row['undefined_dispersion_steps'] for row in rows_by_variant[variant])
    assert all((row['sample_sd_log_price'] != '') == (int(row['trades']) >= 2) for row in rows)
    assert all((row['geometric_mean_price'] != '') == (int(row['trades']) > 0) for row in rows)
    histogram, edges = np.histogram(dispersion, bins=500)
    assert int(histogram.sum()) == len(dispersion)
    for index, count in enumerate(histogram):
        histograms.append({'variant': variant, 'bin_left': float(edges[index]),
                           'bin_right': float(edges[index + 1]), 'count': int(count)})
    windows = {}
    for label in ['early', 'late']:
        selected = [row['windows'][label] for row in rows_by_variant[variant]]
        windows[label] = {'trades_per_run': mean_interval([row['trades'] for row in selected])}
        for metric in ['geometric_mean_price', 'sample_sd_log_price']:
            defined = [row[metric]['mean_over_defined_steps'] for row in selected
                       if row[metric]['defined_steps'] > 0]
            windows[label][metric] = {'defined_runs': len(defined),
                                     'defined_steps': sum(row[metric]['defined_steps'] for row in selected),
                                     'mean_of_defined_run_means': statistics.fmean(defined) if defined else None}
    prices[variant] = {'steps': len(rows), 'undefined_dispersion_steps': len(rows) - len(dispersion),
                       'no_trade_steps': sum(int(row['trades']) == 0 for row in rows),
                       'pooled_defined_dispersion_quantiles': np.quantile(dispersion, [0, .25, .5, .75, 1]).tolist(),
                       'total_trades': sum(int(row['trades']) for row in rows), 'windows': windows}
result = {'reconciliation_sha256': hashlib.sha256(raw).hexdigest(), 'measurement_sha256': input_hashes,
          'survivors': survivors, 'comparisons': comparisons, 'prices': prices,
          'scope': 'New NumPy seeds0–99 with fixed Mesa42. Student-t intervals use100runs, not timesteps. Paired intervals share seed labels but do not assert identical stochastic paths. Histogram uses500bins per variant as author notebook. Historical doubled p-values are not valid two-sided p-values. No equivalence margin or original seeds are available; no paper-level verdict. Concurrent mixed-platform timing is not compared.'}
args.output.mkdir(parents=True, exist_ok=False)
(args.output / 'analysis.json').write_text(json.dumps(result, indent=2, allow_nan=False) + '\n')
with (args.output / 'dispersion-histograms.csv').open('x') as stream:
    writer = csv.DictWriter(stream, fieldnames=list(histograms[0]))
    writer.writeheader()
    writer.writerows(histograms)
print(json.dumps(survivors))
