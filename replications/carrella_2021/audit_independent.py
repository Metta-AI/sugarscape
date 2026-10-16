"""Independently recompute all 150 statistics from completed independent trajectories."""
import argparse
import csv
import gzip
import hashlib
import io
import json
import math
from pathlib import Path
import statistics

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('parameters', type=Path)
parser.add_argument('run', type=Path)
parser.add_argument('mode', choices=['prefix', 'complete'])
parser.add_argument('output', type=Path)
args = parser.parse_args()
assert not args.output.exists()
manifest_bytes = (args.run / 'manifest.json').read_bytes()
manifest = json.loads(manifest_bytes)
parameter_bytes = args.parameters.read_bytes()
assert hashlib.sha256(parameter_bytes).hexdigest() == manifest['parameter_sha256']
parameters = list(csv.DictReader(io.StringIO(parameter_bytes.decode())))
assert len(parameters) == manifest['required_inputs'] == 5000 and manifest['observations_each'] == 501
ledger = (args.run / 'completed.jsonl').read_bytes()
records = [json.loads(line) for line in ledger.splitlines()]
assert 0 < len(records) <= manifest['stop'] - manifest['start']
assert [r['row'] for r in records] == list(range(manifest['start'], manifest['start'] + len(records)))
if args.mode == 'complete':
    assert len(records) == manifest['stop'] - manifest['start']
    complete = json.loads((args.run / 'complete.json').read_text())
    assert complete == {'start': manifest['start'], 'stop': manifest['stop'], 'completed_inputs': len(records)}
summary_snapshot = (args.run / 'summary_statistics.csv').read_bytes()
summary = list(csv.DictReader(io.StringIO(summary_snapshot.decode())))
assert len(summary) >= len(records)
maximum_error = 0.0
extinct = []
for record, reported in zip(records, summary):
    index = record['row']
    original = parameters[index]
    expected = {'population': int(float(original['initial-population'])), 'mutation': float(original['pmut']),
                'maximum_sugar': int(float(original['maximum-sugar-endowment'])),
                'maximum_spice': int(float(original['maximum-spice-endowment'])),
                'reproduction': float(original['wealth-reproduction']), 'seed': int(float(original['random-seed']))}
    assert record['parameters'] == expected and record['archived_seed'] == original['random-seed']
    packed = (args.run / f'row-{index}.csv.gz').read_bytes()
    assert hashlib.sha256(packed).hexdigest() == record['gzip_sha256']
    raw = gzip.decompress(packed)
    assert hashlib.sha256(raw).hexdigest() == record['trajectory_sha256']
    assert raw == (args.run / f'row-{index}.csv').read_bytes()
    reader = csv.DictReader(io.StringIO(raw.decode()))
    names = reader.fieldnames[1:]
    rows = [{k: float(v) for k, v in row.items()} for row in reader]
    assert len(rows) == record['observations'] == 501 and rows[0]['tick'] == 0
    assert rows[0]['count turtles'] == expected['population']
    for i, row in enumerate(rows):
        assert all(math.isfinite(v) for v in row.values())
        assert 0 <= row['count turtles'] <= 2500 and row['count turtles'].is_integer()
        assert -1e-12 <= row['normalized-gini'] <= 1 + 1e-12
        assert 0 <= row['sum [psugar] of patches'] <= 10000 and 0 <= row['sum [pspice] of patches'] <= 10000
        assert row['number_of_prices'] >= 0 and row['number_of_prices'].is_integer() and row['mean_prices'] >= 0
        if i:
            previous = rows[i - 1]
            assert row['tick'] == previous['tick'] + (previous['count turtles'] > 0)
            if previous['count turtles'] == 0:
                assert row == previous
    assert record['last_tick'] == rows[-1]['tick'] and record['last_population'] == rows[-1]['count turtles']
    if rows[-1]['count turtles'] == 0:
        extinct.append(index)
    measured = {}
    for name in names:
        values = [row[name] for row in rows]
        mean = statistics.fmean(values)
        trend = math.fsum((i - 250) * (value - mean) for i, value in enumerate(values)) / math.fsum((i - 250) ** 2 for i in range(501))
        measured.update({'mean_' + name: mean, 'min_' + name: min(values), 'max_' + name: max(values),
                         'last_' + name: values[-1], 'sd_' + name: statistics.pstdev(values), 'trend_' + name: trend})
        measured.update({f'snap_{i}_{name}': values[i] for i in range(25, 500, 25)})
    assert len(measured) == 150 and measured.keys() == reported.keys()
    for name, value in measured.items():
        saved = float(reported[name])
        assert math.isclose(value, saved, rel_tol=1e-10, abs_tol=1e-10), (index, name, value, saved)
        maximum_error = max(maximum_error, abs(value - saved))
report = {'mode': args.mode, 'validated_inputs': len(records), 'statistics_recomputed': 150 * len(records),
          'interval': [manifest['start'], manifest['start'] + len(records)],
          'complete_original_ensemble': args.mode == 'complete' and manifest['start'] == 0 and manifest['stop'] == 5000,
          'maximum_recomputation_absolute_error': maximum_error, 'extinct_inputs': extinct,
          'manifest_sha256': hashlib.sha256(manifest_bytes).hexdigest(), 'ledger_sha256': hashlib.sha256(ledger).hexdigest(),
          'analyzer_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
          'scope': 'Independent standard-library statistic recomputation, input mapping, trajectory integrity, and timing audit. No native-distribution or paper-level equivalence verdict.'}
args.output.mkdir(parents=True, exist_ok=False)
(args.output / 'ledger-snapshot.jsonl').write_bytes(ledger)
(args.output / 'analysis.json').write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps(report))
