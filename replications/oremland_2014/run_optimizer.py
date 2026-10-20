"""Execute a declared reconstruction of Algorithm 1 with real native evaluations."""
import argparse
import hashlib
import json
from pathlib import Path
import random
import subprocess
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class Protocol(BaseModel):
    model_config = ConfigDict(extra='forbid')
    population: int = Field(ge=7, le=100)
    generations: int = Field(ge=2, le=100)
    replicates: int = Field(ge=1, le=1000)
    optimizer_seed: int = Field(ge=0)
    dominance: Literal['dominates-all', 'nondominated']
    radius: float = Field(gt=0, le=1)
    phase: Literal[0, 4]
    clipped: bool
    seconds_per_generation: int = Field(ge=1, le=1800)


class Candidate(BaseModel):
    identity: int
    policy: list[int] = Field(min_length=200, max_length=200)


class NativeResult(BaseModel):
    model_config = ConfigDict(extra='forbid')
    id: str
    seed: int
    phase: Literal[0, 4]
    clipped: bool
    steps: Literal[50.0]
    population: float = Field(ge=0, le=200, allow_inf_nan=False)
    total_tax: float = Field(allow_inf_nan=False)
    debt_refund: float = Field(ge=0, allow_inf_nan=False)
    state_sha256: str = Field(pattern=r'^[0-9a-f]{64}$')
    elapsed_seconds: float = Field(gt=0, allow_inf_nan=False)


def dominates(left, right):
    return all(a >= b for a, b in zip(left, right, strict=True)) and left != right


parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('runtime_manifest', type=Path)
parser.add_argument('protocol', type=Path)
parser.add_argument('output', type=Path)
args = parser.parse_args()
p = Protocol.model_validate_json(args.protocol.read_bytes())
runtime = json.loads(args.runtime_manifest.read_bytes())
command = runtime['command']
assert command[-4] == 'RunPolicyBatch'
model = Path(command[-3])
assert hashlib.sha256(model.read_bytes()).hexdigest() == runtime['model_sha256']
classdir = Path(runtime['compile_command'][runtime['compile_command'].index('-d') + 1])
assert hashlib.sha256((classdir / 'RunPolicyBatch.class').read_bytes()).hexdigest() == runtime['class_sha256']
assert hashlib.sha256((classdir / 'RunPolicyBatch.java').read_bytes()).hexdigest() == runtime['source_sha256']
jarroot = Path(command[command.index('-cp') + 1].split(':')[0]).parent
for name, digest in runtime['jars'].items():
    assert hashlib.sha256((jarroot / name).read_bytes()).hexdigest() == digest
assert all(not (jarroot / name).exists() for name in runtime['missing_declared_jars'])
args.output.mkdir()
(args.output / 'protocol.json').write_text(p.model_dump_json(indent=2) + '\n')
(args.output / 'runtime-manifest.json').write_bytes(args.runtime_manifest.read_bytes())
(args.output / 'run_optimizer.py').write_bytes(Path(__file__).read_bytes())
(args.output / 'choices.json').write_text(json.dumps({
    'initial_policy': 'Independent uniform choices among four rate indices0,1,2,3; rate=index/4.',
    'objectives': 'Maximize summed surviving population and tax revenue over identical seeds0..replicates-1.',
    'reevaluation': 'Every current candidate is reevaluated each generation; no cache or carried objective estimate.',
    'frontier': 'Retain every nondominated candidate, including equal-objective candidates.',
    'tournament': 'Two distinct candidate positions; five distinct comparison positions from the whole current population, including candidates when sampled.',
    'dominance': p.dominance,
    'neighbors': 'Other current candidates with normalized Hamming distance <= radius in policy space.',
    'crossover': 'Independent fair parent choice at each component; second child receives complementary component.',
    'mutation': 'Each component draw is compared with0.20*(generations-generation)/generations; replace with a uniformly selected different rate.',
    'generation_numbering': 'Evaluate generations0..G-1; preserve the final unevaluated next population separately.',
    'odd_slot': 'Keep only the first child when one slot remains; retain both children in the breeding record.',
    'scope': 'Explicit reconstruction choices, not recovered historical optimizer settings. No paper-result claim.'
}, indent=2) + '\n')
rng = random.Random(p.optimizer_seed)
population = [Candidate(identity=i, policy=[rng.randrange(4) for _ in range(200)]) for i in range(p.population)]
next_identity = p.population
for generation in range(p.generations):
    folder = args.output / f'generation-{generation:03d}'
    folder.mkdir()
    (folder / 'population.json').write_text(json.dumps([c.model_dump() for c in population], indent=2) + '\n')
    requests = []
    for candidate in population:
        for seed in range(p.replicates):
            requests.append({'id': f'g{generation}-c{candidate.identity}-s{seed}', 'seed': seed,
                             'phase': p.phase, 'clipped': p.clipped,
                             'policy': [value / 4 for value in candidate.policy]})
    (folder / 'requests.jsonl').write_text(''.join(json.dumps(r) + '\n' for r in requests))
    native_command = command.copy()
    assert native_command[:4] == ['/opt/homebrew/bin/gtimeout', '--signal=TERM', '--kill-after=30', '1800']
    native_command[3] = str(p.seconds_per_generation)
    native_command[-2:] = [str(folder / 'requests.jsonl'), str(folder / 'results.jsonl')]
    with (folder / 'native.log').open('x') as log:
        completed = subprocess.run(native_command, stdout=log, stderr=subprocess.STDOUT,
                                   timeout=p.seconds_per_generation + 60)
    (folder / 'exit.json').write_text(json.dumps({'command': native_command, 'exit_code': completed.returncode}, indent=2) + '\n')
    assert completed.returncode == 0
    results = [NativeResult.model_validate_json(line) for line in (folder / 'results.jsonl').read_text().splitlines()]
    assert len(results) == len(requests)
    for request, result in zip(requests, results, strict=True):
        assert (request['id'], request['seed'], request['phase'], request['clipped']) == (result.id, result.seed, result.phase, result.clipped)
        assert result.population.is_integer() and result.total_tax.is_integer()
    scores = []
    for i in range(p.population):
        batch = results[i * p.replicates:(i + 1) * p.replicates]
        scores.append((sum(int(r.population) for r in batch), sum(int(r.total_tax) for r in batch)))
    frontier = [i for i, score in enumerate(scores) if not any(dominates(other, score) for other in scores)]
    neighbor_counts = [sum(sum(a != b for a, b in zip(candidate.policy, other.policy, strict=True)) / 200 <= p.radius
                           for j, other in enumerate(population) if i != j) for i, candidate in enumerate(population)]
    next_population = [population[i] for i in frontier]
    breeding = []
    mutation_rate = 0.20 * (p.generations - generation) / p.generations
    while len(next_population) < p.population:
        parents = []
        tournaments = []
        for _ in range(2):
            candidates = rng.sample(range(p.population), 2)
            comparison = rng.sample(range(p.population), 5)
            if p.dominance == 'dominates-all':
                eligible = [all(dominates(scores[i], scores[j]) for j in comparison) for i in candidates]
            else:
                eligible = [not any(dominates(scores[j], scores[i]) for j in comparison) for i in candidates]
            if sum(eligible) == 1:
                winner = candidates[eligible.index(True)]
                reason = 'dominance'
            elif neighbor_counts[candidates[0]] != neighbor_counts[candidates[1]]:
                winner = min(candidates, key=lambda i: neighbor_counts[i])
                reason = 'neighbors'
            else:
                winner = rng.choice(candidates)
                reason = 'random'
            parents.append(winner)
            tournaments.append({'candidates': candidates, 'comparison': comparison, 'eligible': eligible,
                                'winner': winner, 'reason': reason})
        mask = [rng.randrange(2) for _ in range(200)]
        children = [[population[parents[bit ^ side]].policy[i] for i, bit in enumerate(mask)] for side in range(2)]
        mutations = []
        for child in children:
            draws = []
            for i, old in enumerate(child):
                draw = rng.random()
                if draw < mutation_rate:
                    child[i] = rng.choice([value for value in range(4) if value != old])
                draws.append(draw)
            mutations.append(draws)
        slots = min(2, p.population - len(next_population))
        additions = [Candidate(identity=next_identity + i, policy=child) for i, child in enumerate(children)]
        next_identity += 2
        next_population.extend(additions[:slots])
        breeding.append({'tournaments': tournaments, 'mask': mask, 'mutation_draws': mutations,
                         'children': [c.model_dump() for c in additions], 'accepted_children': slots})
    report = {'generation': generation, 'scores': scores, 'frontier_indices': frontier,
              'neighbor_counts': neighbor_counts, 'mutation_rate': mutation_rate, 'breeding': breeding,
              'next_population': [c.model_dump() for c in next_population]}
    (folder / 'selection.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({'generation': generation, 'native_runs': len(results), 'frontier_size': len(frontier),
                      'matings': len(breeding)}), flush=True)
    population = next_population
final = {'evaluated_generations': p.generations, 'native_runs': p.generations * p.population * p.replicates,
         'frontier': [{'candidate': json.loads((folder / 'population.json').read_text())[i],
                       'objective_sums': scores[i]} for i in frontier],
         'scope': 'Final evaluated nondominated set; not a proven global frontier or paper replication.'}
(args.output / 'complete.json').write_text(json.dumps(final, indent=2) + '\n')
