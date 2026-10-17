"""Audit a frozen interval of the original runtime archive against native trajectories."""
import argparse
from collections import Counter
import gzip
import hashlib
import json
import math
from pathlib import Path
import zipfile

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('archive', type=Path)
parser.add_argument('run', type=Path)
parser.add_argument('output', type=Path)
parser.add_argument('--allow-prefix', action='store_true')
parser.add_argument('--require-group', action='store_true')
args = parser.parse_args()
manifest = json.loads((args.run / 'manifest.json').read_text())
assert manifest['archive_sha256'] == hashlib.sha256(args.archive.read_bytes()).hexdigest() == '43b1967e9af9d7aac9785258706fd5abec6257235940b85aa811519c0e6ae98a'
assert manifest['release'] == 'b9ca671ab7591c7b3606f2d76c33eda344d626d1'
pins = json.loads(Path(__file__).with_name('source-sha256.json').read_text())
assert manifest['source_sha256'] == pins['source_sha256']
assert hashlib.sha256((args.run / 'run_runtime.py').read_bytes()).hexdigest() == manifest['runner_sha256']
assert manifest['python'].startswith('3.11.14') and manifest['pythonhashseed'] == '0'
start, stop = manifest['start'], manifest['stop']
assert 0 <= start < stop <= 100
assert manifest['model'] in ['rawSugarscape', 'altruisticHalfLookaheadBinary', 'egoisticHalfLookaheadBinary', 'benthamHalfLookaheadBinary']
assert manifest['steps'] in [500, 5000, 50000]
with zipfile.ZipFile(args.archive) as archive:
    original = {name: archive.read(name) for name in archive.namelist() if name.startswith(f"{manifest['steps']}-{manifest['model']}")}
entries = sorted(original)
assert len(entries) == 100 and manifest['entries'] == entries[start:stop]
ledger = (args.run / 'completed.jsonl').read_bytes()
records = [json.loads(line) for line in ledger.splitlines()]
assert 0 < len(records) <= stop - start
assert [row['entry'] for row in records] == entries[start:start+len(records)]
assert [row['index'] for row in records] == list(range(start,start+len(records)))
if not args.allow_prefix:
    assert len(records) == stop - start, 'Incomplete declared interval'
    assert json.loads((args.run / 'complete.json').read_text()) == {'completed_runs': stop - start}
if args.require_group:
    assert start == 0 and stop == len(records) == 100, 'Full group requires100conditions'
counts = Counter({'dead': 0, 'worse': 0, 'better_or_equal': 0})
results = []
for record in records:
    run = args.run / record['entry'].removesuffix('.config')
    assert record['exit_code'] == 0
    assert set(record['files_sha256']) == {'original.config', 'config.json', 'command.json', 'exit.json',
                                         'trajectory.json', 'trajectory.json.gz', 'stdout.log', 'stderr.log'}
    for name, digest in record['files_sha256'].items():
        assert hashlib.sha256((run / name).read_bytes()).hexdigest() == digest
    assert (run / 'original.config').read_bytes() == original[record['entry']]
    config = json.loads(original[record['entry']])
    assert config['seed'] == record['seed'] and config['timesteps'] == manifest['steps']
    assert config['agentDecisionModels'] == [manifest['model']] and config['headlessMode']
    command = json.loads((run / 'command.json').read_text())
    assert command == [manifest['python_executable'], str(Path(manifest['engine']) / 'sugarscape.py'), '--conf', str(run / 'config.json')]
    config['logfile'] = str(run / 'trajectory.json')
    assert json.loads((run / 'config.json').read_text()) == config
    assert json.loads((run / 'exit.json').read_text()) == {'exit_code': 0}
    raw = gzip.decompress((run / 'trajectory.json.gz').read_bytes())
    assert raw == (run / 'trajectory.json').read_bytes()
    rows = json.loads(raw)
    assert [row['timestep'] for row in rows] == list(range(len(rows)))
    assert rows[0]['population'] == config['startingAgents'] == 250
    arrays = {'agentWealths', 'agentTimesToLive', 'agentTimesToLiveAgeLimited'}
    for row in rows:
        assert row['seed'] == record['seed'] and 0 <= row['population'] <= 2500
        assert {key for key, value in row.items() if isinstance(value, list)} == arrays
        assert all(math.isfinite(value) for key, value in row.items() if key not in arrays)
        assert all(math.isfinite(value) for key in arrays for value in row[key])
    final = rows[-1]
    assert final['timestep'] == manifest['steps'] or final['population'] == 0
    assert record['observations'] == len(rows) and record['final_timestep'] == final['timestep']
    assert record['final_population'] == final['population']
    outcome = 'dead' if final['population'] == 0 else 'worse' if final['population'] < 250 else 'better_or_equal'
    counts[outcome] += 1
    results.append({'entry': record['entry'], 'seed': record['seed'], 'observations': len(rows),
                    'final_population': final['population'], 'final_timestep': final['timestep'], 'outcome': outcome,
                    'trajectory_sha256': hashlib.sha256(raw).hexdigest()})
report = {'validated_runs': len(records), 'required_interval_runs': stop - start, 'complete_interval': len(records) == stop - start,
          'complete_group': start == 0 and len(records) == 100, 'model': manifest['model'], 'steps': manifest['steps'],
          'ordinal_interval': [start,start+len(records)], 'counts': dict(counts),
          'observations': sum(row['observations'] for row in results), 'results': results,
          'ledger_sha256': hashlib.sha256(ledger).hexdigest(),
          'manifest_sha256': hashlib.sha256((args.run / 'manifest.json').read_bytes()).hexdigest(),
          'scope': 'Declared original runtime archive interval only. Native plotting puts equality with better. No500seed Table6 verdict.'}
args.output.mkdir(parents=True, exist_ok=False)
(args.output / 'audit.json').write_text(json.dumps(report, indent=2) + '\n')
(args.output / 'ledger-snapshot.jsonl').write_bytes(ledger)
print(json.dumps({key:value for key,value in report.items() if key != 'results'}))
