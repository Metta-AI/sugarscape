from pathlib import Path
import csv
import hashlib
import gzip
import json
import re
import statistics
import sys

root, output = map(Path, sys.argv[1:])
assert not output.exists()
execution = root / 'attempt-002'
assert json.loads((execution / 'complete.json').read_text())['exit_code'] == 0
csv.field_size_limit(20 * 1024**2)
reference = execution / '0-baseline'
rows_checked = history_checked = 0
timings = {'baseline': [[], []], 'cached-appended': [[], []]}
for index, variant in enumerate(['baseline', 'cached-appended', 'cached-appended', 'baseline']):
    run = execution / f'{index}-{variant}'
    assert json.loads((run / 'exit.json').read_text())['exit_code'] == 0
    assert (run / 'results.csv').read_bytes() == (reference / 'results.csv').read_bytes()
    times = re.findall(r'simulation_seconds=(\d+),([0-9.]+)', (run / 'run.log').read_text())
    assert [int(row) for row, _ in times] == [0, 1]
    for row, seconds in times:
        timings[variant][int(row)].append(float(seconds))
    for row in range(2):
        gini = run / f'results.csv.{row}.gini'
        assert gini.read_bytes() == (reference / gini.name).read_bytes()
        assert len(re.findall(r'[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?', gini.read_text())) == 10000
        actual = list(csv.reader((run / f'results.csv.{row}.world').open()))
        expected = list(csv.reader((reference / f'results.csv.{row}.world').open()))
        if variant == 'cached-appended':
            header_index = actual.index(['PATCHES']) + 1
            column = actual[header_index].index('fixed-vision-sets')
            stop = header_index + 1
            while actual[stop]:
                assert len(actual[stop]) == len(actual[header_index])
                stop += 1
            assert stop - header_index - 1 == 2500
            for record in actual[header_index:stop]:
                del record[column]
        assert len(actual) == len(expected)
        assert len(actual[2]) == 1 and re.fullmatch(r'\d+/\d+/\d+ \d+:\d+:\d+:\d+ [-+]\d+', actual[2][0])
        assert actual[:2] == expected[:2] and actual[3:] == expected[3:]
        if index:
            rows_checked += len(actual) - 1
            history_checked += 10000
with gzip.open(root / 'selected.csv.gz', 'rt') as stream:
    archived = list(csv.DictReader(stream))
actual = list(csv.DictReader((reference / 'results.csv').open()))
metric_names = ['gini', 'mwgini', 'moran', 'distance', 'entropy', 'slope', 'rsquared',
                'moranRessource', 'distanceRessource', 'entropyRessource', 'slopeRessource', 'rsquaredRessource']
assert len(archived) == len(actual) == 2
for source, result in zip(archived, actual):
    for metric in metric_names:
        assert abs(float(source[metric]) - float(result[metric])) <= (0 if metric in ['gini', 'mwgini'] else 1e-12)
report = {
    'runs': 8, 'ticks_per_run': 10000, 'populations': [10, 510],
    'history_values_compared_exactly': history_checked,
    'world_rows_compared_exactly': rows_checked,
    'excluded_fields': ['export timestamp', 'new fixed-vision-sets cache column'],
    'archived_metrics_checked': 24, 'archived_gini_exact': True, 'archived_morphology_absolute_tolerance': 1e-12,
    'random_states_exact': True, 'all12_final_metrics_exact': True,
    'simulation_seconds': timings,
    'median_baseline_over_cached_ratios': [statistics.median(timings['baseline'][i]) / statistics.median(timings['cached-appended'][i]) for i in range(2)],
    'file_sha256': {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(execution.rglob('*')) if p.is_file()},
    'scope': 'Two inputs at populations 10 and 510, two repetitions per variant. Exact Gini histories and all original final world fields including RNG; no full-grid fidelity or runtime claim. Setup cache construction and export cost are outside simulation timings. Active scientific runs unchanged.'
}
output.write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps({k: v for k, v in report.items() if k != 'file_sha256'}, indent=2))
