"""Compare complete native trade ticks and mutation-boundary campaigns."""
import argparse
import csv
import hashlib
import json
import math
from pathlib import Path

from model import Agent, Model, Parameters, distance_squared

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('trade', type=Path)
parser.add_argument('mutation', type=Path)
parser.add_argument('output', type=Path)
args = parser.parse_args()
assert not args.output.exists()
parameters = Parameters(population=0, mutation=0, maximum_sugar=10, maximum_spice=10, reproduction=2000, seed=123)
with args.trade.open() as stream:
    trades = list(csv.DictReader(stream))
cases = [(10, 40, 40, 40, 1), (40, 10, 40, 40, 1), (10, 40, 40, 10, 1), (10, 40, 40, 40, 1000)]
assert [int(row['case']) for row in trades] == list(range(4))
trade_results = []
for index, (sugar0, spice0, sugar1, spice1, wealth) in enumerate(cases):
    model = Model(parameters)
    for cell in model.cells:
        model.capacity_sugar[cell] = model.capacity_spice[cell] = model.sugar[cell] = model.spice[cell] = 0
    for identifier, (sugar, spice) in enumerate([(sugar0, spice0), (sugar1, spice1)]):
        agent = Agent(identifier=identifier, x=25 + identifier, y=25, sugar=sugar, spice=spice,
                      sugar_metabolism=1, spice_metabolism=1, vision=1, wealth=wealth)
        model.agents[identifier] = agent
        model.occupied[agent.x, agent.y] = identifier
        model.next_id += 1
    model.mean_price = 7
    model.step()
    actual = {'tick': model.tick, 'population': len(model.agents), 'trades': len(model.prices), 'mean_price': model.mean_price}
    for identifier in [0, 1]:
        for name in ['sugar', 'spice', 'wealth']:
            actual[name + str(identifier)] = getattr(model.agents[identifier], name)
    for name, value in actual.items():
        assert math.isclose(value, float(trades[index][name]), rel_tol=1e-13, abs_tol=1e-13), (index, name, value, trades[index][name])
    assert math.isclose(actual['sugar0'] + actual['sugar1'], sugar0 + sugar1 - 2)
    assert math.isclose(actual['spice0'] + actual['spice1'], spice0 + spice1 - 2)
    trade_results.append({'case': index, 'actual': actual})
with args.mutation.open() as stream:
    native = list(csv.DictReader(stream))
assert [(int(row['parent_metabolism']), int(row['parent_vision']), int(row['seed'])) for row in native] == [
    (m, v, seed) for m, v in [(1, 6), (4, 0)] for seed in range(1, 17)]
independent = []
for row in native:
    metabolism, vision, seed = (int(row[k]) for k in ['parent_metabolism', 'parent_vision', 'seed'])
    model = Model(parameters.model_copy(update={'mutation': 1, 'reproduction': 5, 'seed': seed}))
    for cell in model.cells:
        model.capacity_sugar[cell] = model.capacity_spice[cell] = model.sugar[cell] = model.spice[cell] = 0
    model.agents[0] = Agent(identifier=0, x=25, y=25, sugar=20, spice=20, sugar_metabolism=metabolism,
                            spice_metabolism=metabolism, vision=vision, wealth=20)
    model.occupied[25, 25] = 0
    model.next_id = 1
    model.step()
    parent, child = model.agents[0], model.agents[1]
    observed = {'parent_metabolism': metabolism, 'parent_vision': vision, 'seed': seed,
                'tick': model.tick, 'population': len(model.agents), 'sugar0': parent.sugar, 'spice0': parent.spice,
                'sugar1': child.sugar, 'spice1': child.spice, 'metabolism_sugar1': child.sugar_metabolism,
                'metabolism_spice1': child.spice_metabolism, 'vision1': child.vision,
                'distance1': math.sqrt(distance_squared((parent.x, parent.y), (child.x, child.y))), 'wealth1': child.wealth}
    for state in [row, observed]:
        assert float(state['tick']) == 1 and float(state['population']) == 2
        for name in ['sugar0', 'spice0', 'sugar1', 'spice1', 'wealth1']:
            assert math.isclose(float(state[name]), (20 - metabolism) / 2, abs_tol=1e-13)
        for name in ['metabolism_sugar1', 'metabolism_spice1']:
            assert float(state[name]) in {max(1, metabolism - 1), metabolism + 1}
        assert float(state['vision1']) in {vision - 1, min(6, vision + 1)}
        assert 0 < float(state['distance1']) <= 3
    independent.append(observed)
support = []
for metabolism, vision in [(1, 6), (4, 0)]:
    for name in ['metabolism_sugar1', 'metabolism_spice1', 'vision1']:
        native_values = sorted({float(row[name]) for row in native if int(row['parent_metabolism']) == metabolism})
        independent_values = sorted({row[name] for row in independent if row['parent_metabolism'] == metabolism})
        assert native_values == independent_values
        support.append({'parent_metabolism': metabolism, 'parent_vision': vision, 'trait': name,
                        'native_observed_values': native_values, 'independent_observed_values': independent_values})
report = {'trade_ticks': trade_results, 'mutation_native_ticks': 32, 'mutation_independent_ticks': independent,
          'observed_trait_support': support,
          'input_sha256': {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in [args.trade, args.mutation]},
          'source_sha256': {name: hashlib.sha256(Path(__file__).with_name(name).read_bytes()).hexdigest()
                            for name in ['model.py', 'verify_extensions.py']},
          'limits': 'Four exact complete trade ticks. Mutation campaigns check outcomes, inherited holdings, placement radius, and observed trait support, not paired RNG draws or frequency equivalence. No ensemble-level paper verdict.'}
args.output.mkdir(parents=True, exist_ok=False)
(args.output / 'comparison.json').write_text(json.dumps(report, indent=2) + '\n')
print('Four exact trade ticks and 64 complete mutation-boundary ticks validated')
