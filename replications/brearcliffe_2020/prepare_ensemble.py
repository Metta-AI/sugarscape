"""Freeze both reported parameter interpretations before running full ensembles."""

import argparse
import csv
import hashlib
import itertools
import json
from pathlib import Path

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('author_model', type=Path)
parser.add_argument('new_output', type=Path)
args = parser.parse_args()
original = args.author_model.read_bytes()
assert hashlib.sha256(original).hexdigest() == 'fff5aa29aed92ee4ae04978b643e46d8316e26ca08771adb00c73ee5f2f9b28a'
text = original.decode()
for source in ('random-seed new-seed', 'set learning-rate 0.9', 'set gamma 0.8'):
    assert text.count(source) == 1, source
args.new_output.mkdir()
models = args.new_output / 'models'
models.mkdir()
methods = ['Rule M', 'EC', 'Q-Learning', 'SARSA']
rows = []
seeds = set()
for pair_index, (group_a, group_b) in enumerate(itertools.product(methods, repeat=2)):
    for repetition in range(50):
        label = f'brearcliffe-2020-ensemble-v1/pair-{pair_index:02d}/repeat-{repetition:02d}'
        seed = int.from_bytes(hashlib.sha256(label.encode()).digest()[:4], 'big') & 0x7fffffff
        assert seed not in seeds
        seeds.add(seed)
        for interpretation, learning_rate, gamma in [('released-code', '0.9', '0.8'), ('paper-table', '0.8', '0.9')]:
            name = f'{interpretation}-pair-{pair_index:02d}-repeat-{repetition:02d}'
            model = text.replace('random-seed new-seed', f'random-seed {seed}')
            model = model.replace('set learning-rate 0.9', f'set learning-rate {learning_rate}')
            model = model.replace('set gamma 0.8', f'set gamma {gamma}')
            encoded = model.encode()
            relative = f'models/{name}.nlogo'
            (args.new_output / relative).write_bytes(encoded)
            rows.append({'run_id': name, 'interpretation': interpretation, 'pair_index': pair_index,
                         'group_A': group_a, 'group_B': group_b, 'repetition': repetition,
                         'seed': seed, 'steps': 20000, 'learning_rate': learning_rate, 'gamma': gamma,
                         'model': relative, 'model_sha256': hashlib.sha256(encoded).hexdigest()})
with (args.new_output / 'manifest.csv').open('x', newline='') as file:
    writer = csv.DictWriter(file, fieldnames=list(rows[0]))
    writer.writeheader()
    writer.writerows(rows)
summary = {'runs_per_interpretation': 800, 'interpretations': ['released-code', 'paper-table'],
           'unique_seeds': len(seeds), 'seed_design': 'Same seed within interpretation pairs; distinct across pairings and repetitions.',
           'seed_derivation': 'First four SHA256 bytes of brearcliffe-2020-ensemble-v1/pair-PP/repeat-RR, big endian, masked to 31 bits.',
           'observations_per_run': 20001, 'total_planned_observations': 32001600,
           'author_model_sha256': hashlib.sha256(original).hexdigest(),
           'manifest_sha256': hashlib.sha256((args.new_output / 'manifest.csv').read_bytes()).hexdigest(),
           'execution_status': 'Prepared only; no ensemble runs executed by this command.'}
(args.new_output / 'summary.json').write_text(json.dumps(summary, indent=2) + '\n')
print(json.dumps(summary))
