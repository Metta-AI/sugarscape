"""Independently reconstruct held-out frontier transfer statistics from native records."""
import argparse
import hashlib
import json
import math
from pathlib import Path

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('run', type=Path)
parser.add_argument('output', type=Path)
args = parser.parse_args()
assert not args.output.exists()
plan = json.loads((args.run / 'plan.json').read_bytes())
report = json.loads((args.run / 'complete.json').read_bytes())
seeds = plan['held_out_seeds']
assert len(seeds) >= 2 and len(set(seeds)) == len(seeds)
assert len({g['name'] for g in plan['groups']}) == len(plan['groups'])
rows = []
source_checks = []
shared_inputs = {}
repeated_inputs = 0
for group in plan['groups']:
    folder = args.run / group['name']
    source = Path(group['run'])
    audit = json.loads((folder / 'search-audit.json').read_bytes())
    for filename in ['complete.json', 'protocol.json']:
        assert hashlib.sha256((folder / f'search-{filename}').read_bytes()).hexdigest() == audit['sha256'][filename]
    # Verify the named grid width against the pinned native model, not just the label.
    runtime = json.loads((source / 'runtime-manifest.json').read_bytes())
    assert hashlib.sha256((source / 'runtime-manifest.json').read_bytes()).hexdigest() == audit['sha256']['runtime-manifest.json']
    model = Path(runtime['command'][-3])
    assert hashlib.sha256(model.read_bytes()).hexdigest() == runtime['model_sha256']
    assert f"  resize-world 0 {group['width'] - 1} 0 {group['width'] - 1}\n" in model.read_text()
    source_checks.append({'group': group['name'], 'width': group['width'], 'model_sha256': runtime['model_sha256']})
    protocol = json.loads((folder / 'search-protocol.json').read_bytes())
    assert group['optimizer_seed'] == protocol['optimizer_seed']
    assert plan['phase'] == protocol['phase'] and plan['clipped'] == protocol['clipped']
    assert not set(seeds).intersection(range(protocol['replicates']))
    frontier = json.loads((folder / 'search-complete.json').read_bytes())['frontier']
    assert len(frontier) == audit['final_frontier_size']
    assert json.loads((folder / 'exit.json').read_bytes())['exit_code'] == 0
    requests = [json.loads(x) for x in (folder / 'requests.jsonl').read_bytes().splitlines()]
    results = [json.loads(x) for x in (folder / 'results.jsonl').read_bytes().splitlines()]
    assert len(requests) == len(results) == len(frontier) * len(seeds)
    for i, point in enumerate(frontier):
        candidate = point['candidate']
        values = [[], []]
        for j, seed in enumerate(seeds):
            request, result = requests[i * len(seeds) + j], results[i * len(seeds) + j]
            expected = {'id': f'{group["name"]}-c{candidate["identity"]}-s{seed}', 'seed': seed,
                        'phase': plan['phase'], 'clipped': plan['clipped'], 'policy': [x * .25 for x in candidate['policy']]}
            assert request == expected
            assert all(result[k] == expected[k] for k in ['id', 'seed', 'phase', 'clipped'])
            assert result['steps'] == 50 and 0 <= result['population'] <= 200
            assert all(math.isfinite(result[k]) for k in ['population', 'total_tax', 'debt_refund', 'elapsed_seconds'])
            assert result['debt_refund'] >= 0 and result['elapsed_seconds'] > 0
            assert len(result['state_sha256']) == 64 and int(result['state_sha256'], 16) >= 0
            key = (tuple(candidate['policy']), seed)
            observable = {k: result[k] for k in ['steps', 'population', 'total_tax', 'debt_refund', 'state_sha256']}
            if key in shared_inputs:
                assert shared_inputs[key] == observable
                repeated_inputs += 1
            else:
                shared_inputs[key] = observable
            for k, metric in enumerate(['population', 'total_tax']):
                assert result[metric] == int(result[metric])
                values[k].append(int(result[metric]))
        row = {'group': group['name'], 'identity': candidate['identity'], 'width': group['width'],
               'optimizer_seed': group['optimizer_seed'], 'policy': candidate['policy'], 'samples': len(seeds)}
        for metric, vector in zip(['population', 'total_tax'], values, strict=True):
            total = sum(vector)
            # Exact integer sum-of-squares gives sample variance independently of statistics.stdev.
            variance = (len(vector) * sum(x * x for x in vector) - total * total) / (len(vector) * (len(vector) - 1))
            row[metric] = {'sum': total, 'mean': total / len(vector), 'standard_error': math.sqrt(variance / len(vector))}
        rows.append(row)
assert len(report['policies']) == len(rows)
for actual, expected in zip(report['policies'], rows, strict=True):
    reference = [r for r in rows if r['width'] == 50 and r['optimizer_seed'] == expected['optimizer_seed']]
    assert reference
    a, b = expected['population']['sum'], expected['total_tax']['sum']
    dominated = any((r['population']['sum'] > a and r['total_tax']['sum'] >= b)
                    or (r['population']['sum'] >= a and r['total_tax']['sum'] > b) for r in reference)
    assert actual['dominated_by_full_search'] == dominated
    expected['dominated_by_full_search'] = dominated
    for field in ['group', 'identity', 'width', 'optimizer_seed', 'policy', 'samples']:
        assert actual[field] == expected[field]
    for metric in ['population', 'total_tax']:
        assert actual[metric]['sum'] == expected[metric]['sum']
        for field in ['mean', 'standard_error']:
            assert math.isclose(actual[metric][field], expected[metric][field], rel_tol=1e-12, abs_tol=1e-12)
expected_groups = []
for group in plan['groups']:
    selected = [r for r in rows if r['group'] == group['name']]
    expected_groups.append({'name': group['name'], 'policies': len(selected),
                            'dominated_policies': len([r for r in selected if r['dominated_by_full_search']])})
assert report['groups'] == expected_groups
assert report['native_runs'] == sum(r['samples'] for r in rows)
hashes = {str(f.relative_to(args.run)): hashlib.sha256(f.read_bytes()).hexdigest()
          for f in sorted(args.run.rglob('*')) if f.is_file()}
output = {'native_runs': report['native_runs'], 'policies': len(rows), 'groups': expected_groups,
          'source_models': source_checks, 'repeated_inputs_identical': repeated_inputs, 'sha256': hashes,
          'scope': 'Every held-out request, result, source frontier, mean, standard error and empirical dominance decision checked. Requires original pinned source models for width verification; no global-optimality claim.'}
args.output.write_text(json.dumps(output, indent=2) + '\n')
print(json.dumps({k: output[k] for k in ['native_runs', 'policies', 'groups']}))
