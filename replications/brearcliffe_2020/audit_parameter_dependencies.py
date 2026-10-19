"""Check parameter use and paired-model differences without crediting unexecuted inputs."""

import argparse
import csv
import hashlib
import json
from pathlib import Path
import re

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('author_model', type=Path)
parser.add_argument('prepared', type=Path)
parser.add_argument('new_output', type=Path)
args = parser.parse_args()
original = args.author_model.read_bytes()
assert hashlib.sha256(original).hexdigest() == 'fff5aa29aed92ee4ae04978b643e46d8316e26ca08771adb00c73ee5f2f9b28a'
code = original.decode().split('@#$#@#$#@')[0]
lines = [line.split(';', 1)[0].strip() for line in code.splitlines()]
references = []
procedure = 'declarations'
for number, line in enumerate(lines, 1):
    if line.startswith('to ') or line.startswith('to-report '):
        procedure = line.split()[1]
    if re.search(r'\b(learning-rate|gamma)\b', line):
        references.append({'line': number, 'procedure': procedure, 'text': line})
    if line == 'end':
        procedure = 'declarations'
assert len(references) == 8
assert [r['procedure'] for r in references] == ['declarations'] * 2 + ['setup'] * 2 + ['turtle-learn-q'] * 2 + ['turtle-learn-s'] * 2
for learner, action in [('turtle-learn-q', 'Q-Learning'), ('turtle-learn-s', 'SARSA')]:
    occurrences = [line for line in lines if re.search(r'\b' + learner + r'\b', line)]
    assert occurrences == [f'if group-A-action = "{action}" [ {learner} ]',
                           f'if group-B-action = "{action}" [ {learner} ]', f'to {learner}']
assert not any(re.search(r'\bset group-[AB]-action\b', line) for line in lines)
assert [line for line in lines if re.search(r'\b(run|runresult)\b', line)] == ['run visualization'] * 3
assert not any(re.search(r'\bset visualization\b', line) for line in lines)
start = lines.index('to no-visualization')
assert lines[start:start + 4] == ['to no-visualization',
                                'if breed = group-A [ set color blue ]',
                                'if breed = group-B [ set color red ]', 'end']
recorder = Path(__file__).with_name('Replay.java')
assert 'set visualization \\"no-visualization\\"' in recorder.read_text()
manifest = args.prepared / 'manifest.csv'
with manifest.open() as file:
    rows = list(csv.DictReader(file))
assert len(rows) == 1600
by_key = {(r['interpretation'], r['pair_index'], r['repetition']): r for r in rows}
assert len(by_key) == 1600
pairs = []
for index in range(16):
    for repetition in range(50):
        released = by_key[('released-code', str(index), str(repetition))]
        paper = by_key[('paper-table', str(index), str(repetition))]
        assert released['seed'] == paper['seed']
        left = (args.prepared / released['model']).read_bytes()
        right = (args.prepared / paper['model']).read_bytes()
        assert hashlib.sha256(left).hexdigest() == released['model_sha256']
        assert hashlib.sha256(right).hexdigest() == paper['model_sha256']
        assert left.count(b'set learning-rate 0.9') == left.count(b'set gamma 0.8') == 1
        assert left.replace(b'set learning-rate 0.9', b'set learning-rate 0.8').replace(b'set gamma 0.8', b'set gamma 0.9') == right
    pairs.append({'pair_index': index, 'group_A': released['group_A'], 'group_B': released['group_B'],
                  'uses_disputed_parameters': any(r in ['Q-Learning', 'SARSA'] for r in [released['group_A'], released['group_B']]),
                  'paired_inputs_checked': 50})
assert [r['pair_index'] for r in pairs if not r['uses_disputed_parameters']] == [0, 1, 4, 5]
report = {'author_model_sha256': hashlib.sha256(original).hexdigest(),
          'recorder_source_sha256': hashlib.sha256(recorder.read_bytes()).hexdigest(),
          'manifest_sha256': hashlib.sha256(manifest.read_bytes()).hexdigest(),
          'parameter_references': references, 'pairings': pairs, 'paired_models_checked': 800,
          'parameter_sensitive_pairings': 12, 'parameter_insensitive_pairings': 4,
          'limits': ['Pinned-source control-flow audit under Replay.java no-visualization setup, not a general NetLogo analyzer.',
                     'Prepared variants differ only in two literal assignments and retain matched seeds.',
                     'No paired runtime sensitivity execution is performed by this command.',
                     'Frozen manifests, coverage counts, active reservations, and remaining work are unchanged.',
                     'The source finding permits planning shared evidence for four unaffected pairings; it does not credit 200 unexecuted paper-table inputs.']}
args.new_output.mkdir()
(args.new_output / 'audit.json').write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps({'paired_models_checked': 800, 'sensitive_pairings': 12, 'insensitive_pairings': 4}))
