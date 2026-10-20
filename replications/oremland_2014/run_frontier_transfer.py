"""Reevaluate every audited search frontier on the full model with held-out seeds."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import statistics
import subprocess

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('plan', type=Path)
parser.add_argument('output', type=Path)
args = parser.parse_args()
plan = json.loads(args.plan.read_bytes())
assert len({g['name'] for g in plan['groups']}) == len(plan['groups'])
seeds = plan['held_out_seeds']
assert len(seeds) >= 2 and len(set(seeds)) == len(seeds)
assert all(isinstance(s, int) and 0 <= s < 2**31 for s in seeds)
runtime = json.loads(Path(plan['runtime_manifest']).read_bytes())
command = runtime['command']
assert command[-4] == 'RunPolicyBatch'
model = Path(command[-3])
assert hashlib.sha256(model.read_bytes()).hexdigest() == runtime['model_sha256'] == '1cc6ee9db0852ea2a071004aa31eb797a06131b434cffc82f697993057aca816'
assert hashlib.sha256(model.with_name('sugar-map.txt').read_bytes()).hexdigest() == 'cd9b4661c8813d3e268995676d5ba84394ee813986adb0d657dc9be4a1fab675'
classdir = Path(runtime['compile_command'][runtime['compile_command'].index('-d') + 1])
for name, key in [('RunPolicyBatch.class', 'class_sha256'), ('RunPolicyBatch.java', 'source_sha256')]:
    assert hashlib.sha256((classdir / name).read_bytes()).hexdigest() == runtime[key]
jarroot = Path(command[command.index('-cp') + 1].split(':')[0]).parent
for name, digest in runtime['jars'].items():
    assert hashlib.sha256((jarroot / name).read_bytes()).hexdigest() == digest
assert all(not (jarroot / name).exists() for name in runtime['missing_declared_jars'])
# Validate the entire frozen source set before starting any native work.
for group in plan['groups']:
    run = Path(group['run'])
    audit = json.loads(Path(group['audit']).read_bytes())
    for name, digest in audit['sha256'].items():
        assert hashlib.sha256((run / name).read_bytes()).hexdigest() == digest
    protocol = json.loads((run / 'protocol.json').read_bytes())
    assert protocol['optimizer_seed'] == group['optimizer_seed']
    assert not set(seeds).intersection(range(protocol['replicates']))
    assert protocol['phase'] == plan['phase'] and protocol['clipped'] == plan['clipped']
    done = json.loads((run / 'complete.json').read_bytes())
    assert done['evaluated_generations'] == protocol['generations']
    assert done['native_runs'] == protocol['population'] * protocol['generations'] * protocol['replicates']
    assert done['native_runs'] == audit['native_runs'] and len(done['frontier']) == audit['final_frontier_size']
assert all(any(g['width'] == 50 and g['optimizer_seed'] == group['optimizer_seed'] for g in plan['groups']) for group in plan['groups'])
args.output.mkdir()
(args.output / 'plan.json').write_bytes(args.plan.read_bytes())
(args.output / 'runtime-manifest.json').write_bytes(Path(plan['runtime_manifest']).read_bytes())
(args.output / 'run_frontier_transfer.py').write_bytes(Path(__file__).read_bytes())
rows = []
for group in plan['groups']:
    folder = args.output / group['name']
    folder.mkdir()
    run = Path(group['run'])
    for filename in ['complete.json', 'protocol.json']:
        (folder / f'search-{filename}').write_bytes((run / filename).read_bytes())
    (folder / 'search-audit.json').write_bytes(Path(group['audit']).read_bytes())
    frontier = json.loads((run / 'complete.json').read_bytes())['frontier']
    requests = [{'id': f'{group["name"]}-c{point["candidate"]["identity"]}-s{seed}', 'seed': seed,
                 'phase': plan['phase'], 'clipped': plan['clipped'],
                 'policy': [x / 4 for x in point['candidate']['policy']]}
                for point in frontier for seed in seeds]
    (folder / 'requests.jsonl').write_text(''.join(json.dumps(r) + '\n' for r in requests))
    native = command.copy()
    assert native[:4] == ['/opt/homebrew/bin/gtimeout', '--signal=TERM', '--kill-after=30', '1800']
    native[-2:] = [str(folder / 'requests.jsonl'), str(folder / 'results.jsonl')]
    with (folder / 'native.log').open('x') as log:
        completed = subprocess.run(native, stdout=log, stderr=subprocess.STDOUT, timeout=1860)
    (folder / 'exit.json').write_text(json.dumps({'command': native, 'exit_code': completed.returncode}, indent=2) + '\n')
    assert completed.returncode == 0
    results = [json.loads(line) for line in (folder / 'results.jsonl').read_text().splitlines()]
    assert len(results) == len(requests)
    for request, result in zip(requests, results, strict=True):
        assert all(request[k] == result[k] for k in ['id', 'seed', 'phase', 'clipped'])
        assert result['steps'] == 50 and 0 <= result['population'] <= 200
        assert all(math.isfinite(result[k]) for k in ['population', 'total_tax', 'debt_refund', 'elapsed_seconds'])
        assert result['population'] == int(result['population']) and result['total_tax'] == int(result['total_tax'])
        assert result['debt_refund'] >= 0 and result['elapsed_seconds'] > 0
        assert len(result['state_sha256']) == 64 and int(result['state_sha256'], 16) >= 0
    for i, point in enumerate(frontier):
        batch = results[i * len(seeds):(i + 1) * len(seeds)]
        row = {'group': group['name'], 'width': group['width'], 'optimizer_seed': group['optimizer_seed'],
               'identity': point['candidate']['identity'], 'policy': point['candidate']['policy'], 'samples': len(batch)}
        for metric in ['population', 'total_tax']:
            values = [int(r[metric]) for r in batch]
            row[metric] = {'sum': sum(values), 'mean': statistics.mean(values), 'standard_error': statistics.stdev(values) / math.sqrt(len(values))}
        rows.append(row)
    print(json.dumps({'group': group['name'], 'policies': len(frontier), 'native_runs': len(results)}), flush=True)
for row in rows:
    reference = [r for r in rows if r['width'] == 50 and r['optimizer_seed'] == row['optimizer_seed']]
    row['dominated_by_full_search'] = any(
        all(r[k]['sum'] >= row[k]['sum'] for k in ['population', 'total_tax'])
        and any(r[k]['sum'] > row[k]['sum'] for k in ['population', 'total_tax']) for r in reference)
summary = {'native_runs': sum(r['samples'] for r in rows), 'policies': rows,
           'groups': [{'name': g['name'], 'policies': sum(r['group'] == g['name'] for r in rows),
                       'dominated_policies': sum(r['group'] == g['name'] and r['dominated_by_full_search'] for r in rows)} for g in plan['groups']],
           'scope': 'Held-out empirical dominance against the finite full-size search frontier, not global optimality or historical numerical identity.'}
(args.output / 'complete.json').write_text(json.dumps(summary, indent=2) + '\n')
