"""Run the predeclared reproduction-boundary diagnostic in a fresh directory."""
import argparse
import difflib
import hashlib
import json
from pathlib import Path
import subprocess
import time

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('output', type=Path)
args = parser.parse_args()
root = Path(__file__).resolve().parent
source = (root / 'simulate.cpp').read_text()
assert source.count('agent.age >= 1') == 1 and source.count('agent.wealth >= birth_cost') == 1
args.output.mkdir(parents=True, exist_ok=False)
variants = ['baseline', 'strict-age', 'strict-wealth', 'strict-both']
manifest = {'source_sha256': hashlib.sha256(source.encode()).hexdigest(),
            'protocol_sha256': hashlib.sha256((root / 'REPRODUCTION_BOUNDARIES.md').read_bytes()).hexdigest(),
            'runner_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            'seeds': list(range(111, 121)), 'cycles': 100000, 'record_every': 100,
            'variants': {}, 'required_runs': 80}
for variant in variants:
    changed = source
    if variant in ['strict-age', 'strict-both']:
        changed = changed.replace('agent.age >= 1', 'agent.age > 1')
    if variant in ['strict-wealth', 'strict-both']:
        changed = changed.replace('agent.wealth >= birth_cost', 'agent.wealth > birth_cost')
    path = args.output / (variant + '.cpp')
    path.write_text(changed)
    (args.output / (variant + '.patch')).write_text(''.join(difflib.unified_diff(
        source.splitlines(True), changed.splitlines(True), fromfile='simulate.cpp', tofile=path.name)))
    binary = args.output / variant
    command = ['clang++', '-std=c++17', '-O2', '-Wall', '-Wextra', '-Werror', str(path), '-o', str(binary)]
    subprocess.run(command, check=True)
    manifest['variants'][variant] = {'command': command, 'source_sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
                                      'binary_sha256': hashlib.sha256(binary.read_bytes()).hexdigest()}
manifest['compiler'] = subprocess.check_output(['clang++', '--version'], text=True)
(args.output / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
with (args.output / 'completed.jsonl').open('x') as ledger:
    for scenario, infertility, cost in [('low-fertility', 85, 0), ('birth-cost', 10, 40)]:
        for seed in manifest['seeds']:
            for variant in variants:
                stem = f'{scenario}-{seed}-{variant}'
                aggregate = args.output / (stem + '.csv')
                observations = args.output / (stem + '-observations.csv')
                command = [str(args.output / variant), str(seed), str(infertility), str(cost), '100000', '100', str(observations)]
                started = time.monotonic()
                with aggregate.open('x') as stdout, (args.output / (stem + '.stderr')).open('x') as stderr:
                    result = subprocess.run(command, stdout=stdout, stderr=stderr)
                record = {'scenario': scenario, 'seed': seed, 'variant': variant, 'command': command,
                          'exit_code': result.returncode, 'elapsed_seconds': time.monotonic() - started,
                          'hashes': {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in [aggregate, observations]}}
                ledger.write(json.dumps(record) + '\n')
                ledger.flush()
                assert result.returncode == 0, record
                print(stem, 'completed', flush=True)
(args.output / 'complete.json').write_text(json.dumps({'completed_runs': 80}) + '\n')
