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
protocol = json.loads((root / 'protocol.json').read_text())
assert hashlib.sha256((root / 'selected.csv.gz').read_bytes()).hexdigest() == protocol['selected_sha256']
for name, digest in protocol['source_hashes'].items():
    assert hashlib.sha256((root / name).read_bytes()).hexdigest() == digest
with gzip.open(root / 'selected.csv.gz', 'rt') as stream:
    assert list(csv.DictReader(stream)) == protocol['source_rows']
assert [float(row['population']) for row in protocol['source_rows']] == list(range(10, 511, 50))
assert [int(row['id']) for row in protocol['source_rows']] == list(range(0, 41, 4))
baseline = root / 'baseline'
cached = root / 'cached-appended'
restored_model = (cached / 'HEADLESS_Sugarscape.nlogo').read_text().replace('  fixed-vision-sets\n', '')
assert restored_model == (baseline / 'HEADLESS_Sugarscape.nlogo').read_text()
cache_setup = """    set fixed-vision-sets []
    let offsets []
    let radius 1
    while [radius <= max-vision] [
      set offsets sentence offsets (list (list 0 radius) (list radius 0) (list 0 (- radius)) (list (- radius) 0))
      set fixed-vision-sets lput (patches at-points offsets) fixed-vision-sets
      set radius radius + 1
    ]
"""
assert (cached / 'setup.nls').read_text().replace(cache_setup, '') == (baseline / 'setup.nls').read_text()
assert (cached / 'turtles.nls').read_text().replace('(item (vision - 1) fixed-vision-sets)', '(patches at-points vision-points)') == (baseline / 'turtles.nls').read_text()
for source in baseline.rglob('*'):
    if source.is_file() and source.name not in ['HEADLESS_Sugarscape.nlogo', 'setup.nls', 'turtles.nls']:
        assert source.read_bytes() == (cached / source.relative_to(baseline)).read_bytes()
execution = root / 'attempt-001'

assert json.loads((execution / 'complete.json').read_text())['exit_code'] == 0
csv.field_size_limit(20 * 1024**2)
reference = execution / '0-baseline'
rows_checked = history_checked = 0
process_seconds = {'baseline': [], 'cached-appended': []}
timings = {'baseline': [[] for _ in range(11)], 'cached-appended': [[] for _ in range(11)]}
for index, variant in enumerate(['baseline', 'cached-appended', 'cached-appended', 'baseline']):
    run = execution / f'{index}-{variant}'
    receipt = json.loads((run / 'exit.json').read_text())
    assert receipt['exit_code'] == 0
    process_seconds[variant].append(receipt['elapsed_seconds'])
    assert (run / 'results.csv').read_bytes() == (reference / 'results.csv').read_bytes()
    times = re.findall(r'simulation_seconds=(\d+),([0-9.]+)', (run / 'run.log').read_text())
    assert [int(row) for row, _ in times] == list(range(11))
    for row, seconds in times:
        timings[variant][int(row)].append(float(seconds))
    for row in range(11):
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
assert len(archived) == len(actual) == 11
for source, result in zip(archived, actual):
    for metric in metric_names:
        assert abs(float(source[metric]) - float(result[metric])) <= (0 if metric in ['gini', 'mwgini'] else 1e-12)
report = {
    'runs': 44, 'ticks_per_run': 10000, 'populations': list(range(10, 511, 50)),
    'history_values_compared_exactly': history_checked,
    'world_rows_compared_exactly': rows_checked,
    'excluded_fields': ['export timestamp', 'new fixed-vision-sets cache column'],
    'archived_metrics_checked': 132, 'archived_gini_exact': True, 'archived_morphology_absolute_tolerance': 1e-12,
    'random_states_exact': True, 'all12_final_metrics_exact': True,
    'simulation_seconds': timings,
    'complete_process_seconds': process_seconds,
    'median_process_baseline_over_cached_ratio': statistics.median(process_seconds['baseline']) / statistics.median(process_seconds['cached-appended']),
    'model_source_hashes_verified': len(protocol['source_hashes']),
    'frozen_selection_exact': True,
    'only_declared_cache_source_edits': True,
    'median_baseline_over_cached_ratios': [statistics.median(timings['baseline'][i]) / statistics.median(timings['cached-appended'][i]) for i in range(11)],
    'file_sha256': {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(execution.rglob('*')) if p.is_file()},
    'scope': 'Eleven inputs across every population level and eleven distinct layouts, two repetitions per variant. Exact Gini histories and all original final world fields including RNG; no full-grid fidelity or runtime claim. Setup cache construction and export cost are outside simulation timings. Active scientific runs unchanged.'
}
output.write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps({k: v for k, v in report.items() if k != 'file_sha256'}, indent=2))
