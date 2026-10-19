from pathlib import Path
import collections
import csv
import hashlib
import json
import re
import subprocess
import sys

root, output = map(Path, sys.argv[1:])
assert not output.exists()
reference = Path('/Users/relh/Code/workspace/sugarscape-replication-evidence/raimbault-gini-qualification-001/attempt-002/0-baseline')
assert json.loads((root / 'terminal.json').read_text())['exit_code'] == 0
assert (root / 'results.csv').read_bytes() == (reference / 'results.csv').read_bytes()
csv.field_size_limit(10 * 1024**2)
world_rows = 0
for i in range(2):
    actual = root / f'results.csv.{i}.gini'
    assert actual.read_bytes() == (reference / actual.name).read_bytes()
    assert len(re.findall(r'[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?', actual.read_text())) == 10000
    actual = list(csv.reader((root / f'results.csv.{i}.world').open()))
    expected = list(csv.reader((reference / f'results.csv.{i}.world').open()))
    assert len(actual) == len(expected)
    assert len(actual[2]) == 1 and re.fullmatch(r'\d+/\d+/\d+ \d+:\d+:\d+:\d+ [-+]\d+', actual[2][0])
    assert actual[:2] == expected[:2] and actual[3:] == expected[3:]
    world_rows += len(actual) - 1
samples = json.loads((root / 'samples.json').read_text())['recording']['events']
summary = subprocess.check_output(['/opt/homebrew/opt/openjdk@11/bin/jfr', 'summary', str(root / 'execution.jfr')], text=True, timeout=60)
assert int(re.search(r'jdk.ExecutionSample\s+(\d+)', summary).group(1)) == len(samples)
threads = collections.Counter()
leaf = collections.Counter()
groups = {name: 0 for name in ['turtle_move', 'regrow_patches', 'gini_update', 'landscape_generation']}
prefixes = {'turtle_move': '_asm_procedureturtlemove', 'regrow_patches': '_asm_procedureregrowpatches',
            'gini_update': '_asm_procedureupdatelorenzandgini', 'landscape_generation': '_asm_proceduregosynthpattern'}
for event in samples:
    assert event['type'] == 'jdk.ExecutionSample'
    value = event['values']
    threads[value['sampledThread']['javaName']] += 1
    names = [f['method']['type']['name'] + '.' + f['method']['name'] for f in value['stackTrace']['frames']]
    leaf[names[0]] += 1
    for name, prefix in prefixes.items():
        groups[name] += int(any(prefix in method for method in names))
paths = sorted(p for p in root.iterdir() if p.name in ['execution.jfr', 'samples.json', 'run.py', 'run.log', 'terminal.json', 'protocol.json'] or p.name.startswith('results.csv'))
report = {'full_horizon_runs': 2, 'populations': [10, 510], 'ticks_each': 10000,
          'gini_history_values_exact': 20000, 'exported_world_rows_exact_excluding_timestamps': world_rows,
          'random_states_exact': True, 'all12_metrics_exact_for_both_inputs': True,
          'execution_samples': len(samples), 'threads': dict(threads), 'inclusive_procedure_sample_counts': groups,
          'top_leaf_sample_counts': dict(leaf.most_common(20)),
          'file_sha256': {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in paths},
          'reference_sha256': {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(reference.glob('results.csv*'))},
          'scope': 'Single instrumented execution of two qualified inputs, including setup and reporting. Inclusive sample groups may overlap; sample counts are not independent timing measurements or full-grid performance estimates. Unmodified scientific state matches prior baseline. Movement candidate construction is a profiling lead; no optimized implementation, production change, cheaper-grid claim or paper completion.'}
output.write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps({k: report[k] for k in ['execution_samples', 'threads', 'inclusive_procedure_sample_counts', 'gini_history_values_exact', 'exported_world_rows_exact_excluding_timestamps']}, indent=2))
