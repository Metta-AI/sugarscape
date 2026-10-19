"""Post-discrepancy diagnostic of extinction-row and fixed-horizon death-rate means."""
from pathlib import Path
import hashlib
import json
import statistics

root = Path(__file__).resolve().parent
repo = Path('/Users/relh/Code/workspace/sugarscape-blueprints/replications/blueprints_2024/results')
source = repo / 'heterogeneous50-death-rate-2026-10-19'
records = json.loads((source / 'per-run.json').read_text())
prior = json.loads((source / 'summary.json').read_text())
assert len(records) == len({row['entry'] for row in records}) == 500
assert sum(row['observations'] for row in records) == 1781148
lo, hi = prior['figure20_target']['ink_percent_interval']
results = {}
for key in records[0]['definitions']:
    exclude = int('/exclude_initial' in key)
    horizon_rows = 5001 - exclude
    values = {name: [] for name in ['positive_population_only', 'observed_zero_assigned', 'fixed_horizon_zero_extended']}
    for row in records:
        item = row['definitions'][key]
        observed_rows = row['observations'] - exclude
        assert item['positive_rows'] + item['zero_population_rows'] == observed_rows
        assert item['zero_population_rows'] in (0, 1)
        assert 0 < observed_rows <= horizon_rows
        denominators = {'positive_population_only': item['positive_rows'],
                        'observed_zero_assigned': observed_rows,
                        'fixed_horizon_zero_extended': horizon_rows}
        for name, denominator in denominators.items():
            values[name].append(100 * item['sum_step_ratios'] / denominator)
    for name, data in values.items():
        median = statistics.median(data)
        results[key + '/' + name] = {'inputs': len(data), 'median_percent': median, 'within_paper_ink': lo <= median <= hi}
    assert results[key + '/positive_population_only']['median_percent'] == prior['definitions'][key + '/mean_of_step_ratios']['median_percent']
paths = [source / 'per-run.json', source / 'summary.json', repo / 'death-plot-history-2026-10-19/cc0408a-plot.py']
report = {'inputs': 500, 'native_observations': 1781148, 'native_extinctions': 150,
          'future_zero_rows': sum(5001 - row['observations'] for row in records),
          'terminal_zero_population_rows': sum(row['definitions']['all_reported_causes/include_initial']['zero_population_rows'] for row in records),
          'all_cause_deaths_at_zero_population': sum(row['definitions']['all_reported_causes/include_initial']['deaths_at_zero_population'] for row in records),
          'figure20_ink_interval_percent': [lo, hi], 'definitions': results,
          'source_sha256': {str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in paths},
          'scope': 'Exploratory extinction handling diagnostic using previously native-audited per-run accumulators. All500 seeds retained. The historical helper zero-fills arrays and assigns zero when population is zero, but its aggregation across runs is different; these per-run temporal means are not claimed as the Figure20 implementation. No original data or primary result changes; no new simulation or paper-completion credit.'}
(root / 'summary.json').write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps(report, indent=2))
