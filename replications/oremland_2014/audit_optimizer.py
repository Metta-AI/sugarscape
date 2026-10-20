"""Replay every native objective and genetic decision in a completed optimizer run."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import random


parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('run', type=Path)
parser.add_argument('output', type=Path)
args = parser.parse_args()
assert not args.output.exists()
p = json.loads((args.run / 'protocol.json').read_bytes())
done = json.loads((args.run / 'complete.json').read_bytes())
rng = random.Random(p['optimizer_seed'])
expected = [{'identity': i, 'policy': [rng.randrange(4) for _ in range(200)]} for i in range(p['population'])]
next_identity = p['population']
total_native = total_matings = total_mutations = 0
reasons = {'dominance': 0, 'neighbors': 0, 'random': 0}
for g in range(p['generations']):
    folder = args.run / f'generation-{g:03d}'
    population = json.loads((folder / 'population.json').read_bytes())
    assert population == expected and len({c['identity'] for c in population}) == p['population']
    assert json.loads((folder / 'exit.json').read_bytes())['exit_code'] == 0
    requests = [json.loads(line) for line in (folder / 'requests.jsonl').read_text().splitlines()]
    results = [json.loads(line) for line in (folder / 'results.jsonl').read_text().splitlines()]
    assert len(requests) == len(results) == p['population'] * p['replicates']
    scores = [[0, 0] for _ in population]
    for i, (request, result) in enumerate(zip(requests, results, strict=True)):
        position, seed = divmod(i, p['replicates'])
        candidate = population[position]
        assert request == {'id': f'g{g}-c{candidate["identity"]}-s{seed}', 'seed': seed,
                           'phase': p['phase'], 'clipped': p['clipped'],
                           'policy': [x / 4 for x in candidate['policy']]}
        assert all(result[k] == request[k] for k in ('id', 'seed', 'phase', 'clipped'))
        assert result['steps'] == 50
        assert all(math.isfinite(result[k]) for k in ('population', 'total_tax', 'debt_refund', 'elapsed_seconds'))
        assert 0 <= result['population'] <= 200 and result['population'] == int(result['population'])
        assert result['total_tax'] == int(result['total_tax']) and result['debt_refund'] >= 0
        assert len(result['state_sha256']) == 64 and int(result['state_sha256'], 16) >= 0
        scores[position][0] += int(result['population'])
        scores[position][1] += int(result['total_tax'])
    total_native += len(results)
    # Explicit two-objective weak/strict inequalities, independent of the producer helper.
    dominance = [[a[0] >= b[0] and a[1] >= b[1] and (a[0] > b[0] or a[1] > b[1])
                  for b in scores] for a in scores]
    frontier = [i for i in range(len(population)) if not any(row[i] for row in dominance)]
    neighbors = [sum(sum(x != y for x, y in zip(a['policy'], b['policy'], strict=True)) <= 200 * p['radius']
                     for j, b in enumerate(population) if i != j) for i, a in enumerate(population)]
    selection = json.loads((folder / 'selection.json').read_bytes())
    assert selection['generation'] == g and selection['scores'] == scores
    assert selection['frontier_indices'] == frontier and selection['neighbor_counts'] == neighbors
    rate = (p['generations'] - g) * .20 / p['generations']
    assert abs(selection['mutation_rate'] - rate) < 1e-15
    expected = [population[i] for i in frontier]
    for mating in selection['breeding']:
        assert len(expected) < p['population'] and len(mating['tournaments']) == 2
        parents = []
        for tournament in mating['tournaments']:
            candidates = rng.sample(range(p['population']), 2)
            subset = rng.sample(range(p['population']), 5)
            assert tournament['candidates'] == candidates and tournament['comparison'] == subset
            if p['dominance'] == 'dominates-all':
                qualifies = [sum(dominance[i][j] for j in subset) == 5 for i in candidates]
            else:
                assert p['dominance'] == 'nondominated'
                qualifies = [sum(dominance[j][i] for j in subset) == 0 for i in candidates]
            assert tournament['eligible'] == qualifies
            a, b = candidates
            if qualifies[0] != qualifies[1]:
                winner = a if qualifies[0] else b
                reason = 'dominance'
            elif neighbors[a] != neighbors[b]:
                winner = a if neighbors[a] < neighbors[b] else b
                reason = 'neighbors'
            else:
                winner = rng.choice(candidates)
                reason = 'random'
            assert tournament['winner'] == winner and tournament['reason'] == reason
            reasons[reason] += 1
            parents.append(population[winner]['policy'])
        mask = [rng.randrange(2) for _ in range(200)]
        assert mating['mask'] == mask
        children = [[], []]
        for i, bit in enumerate(mask):
            children[0].append(parents[bit][i])
            children[1].append(parents[1 - bit][i])
        for side in range(2):
            assert len(mating['mutation_draws'][side]) == 200
            for i in range(200):
                draw = rng.random()
                assert mating['mutation_draws'][side][i] == draw
                if draw < selection['mutation_rate']:
                    children[side][i] = rng.choice([x for x in range(4) if x != children[side][i]])
                    total_mutations += 1
        records = [{'identity': next_identity + side, 'policy': children[side]} for side in range(2)]
        next_identity += 2
        assert mating['children'] == records
        accepted = min(2, p['population'] - len(expected))
        assert mating['accepted_children'] == accepted
        expected.extend(records[:accepted])
        total_matings += 1
    assert len(expected) == p['population'] and selection['next_population'] == expected
assert done['evaluated_generations'] == p['generations'] and done['native_runs'] == total_native
assert done['frontier'] == [{'candidate': population[i], 'objective_sums': scores[i]} for i in frontier]
assert total_matings > 0 and total_mutations > 0, 'Qualification must exercise the genetic operators.'
hashes = {str(path.relative_to(args.run)): hashlib.sha256(path.read_bytes()).hexdigest()
          for path in sorted(args.run.rglob('*')) if path.is_file()}
args.output.write_text(json.dumps({'native_runs': total_native, 'evaluated_generations': p['generations'],
                                  'matings': total_matings, 'mutated_components': total_mutations,
                                  'parent_selection_reasons': reasons, 'final_frontier_size': len(frontier),
                                  'sha256': hashes,
                                  'scope': 'Complete native optimization workflow and genetic-decision replay under declared choices; no historical-parameter or global-optimality claim.'}, indent=2) + '\n')
print(json.dumps({'native_runs': total_native, 'matings': total_matings, 'mutations': total_mutations,
                  'selection_reasons': reasons, 'final_frontier_size': len(frontier)}))
