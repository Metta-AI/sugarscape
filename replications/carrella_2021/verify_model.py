"""Compare complete independent-model ticks and all map cells with native probes."""
import argparse
import csv
import hashlib
import json
import math
from pathlib import Path

from model import Agent, Model, Parameters

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('native', type=Path)
parser.add_argument('output', type=Path)
args = parser.parse_args()
assert not args.output.exists()
parameters = Parameters(population=0, mutation=0, maximum_sugar=10, maximum_spice=10, reproduction=5, seed=123)
model = Model(parameters)
with (args.native / 'map.csv').open() as stream:
    cells = list(csv.DictReader(stream))
assert len(cells) == 2500
assert len({(int(c['x']), int(c['y'])) for c in cells}) == 2500
for cell in cells:
    position = int(cell['x']), int(cell['y'])
    assert model.capacity_sugar[position] == int(cell['sugar'])
    assert model.capacity_spice[position] == int(cell['spice'])
with (args.native / 'results.csv').open() as stream:
    reference = list(csv.DictReader(stream))
assert [row['case'] for row in reference] == ['cached-1', 'cached-10', 'equal-rates-retained-potentials']
comparisons = []
for row in reference:
    equal_case = row['case'] == 'equal-rates-retained-potentials'
    cached = 1 if row['case'] == 'cached-1' or equal_case else 10
    model = Model(parameters.model_copy(update={'reproduction': 100 if equal_case else 5}))
    for cell in model.cells:
        model.capacity_sugar[cell] = model.capacity_spice[cell] = model.sugar[cell] = model.spice[cell] = 0
    for identifier in range(2 if equal_case else 1):
        agent = Agent(identifier=identifier, x=25 + identifier, y=25, sugar=10, spice=10,
                      sugar_metabolism=1, spice_metabolism=1, vision=1, wealth=cached,
                      potential_sugar=20 if equal_case else 0, potential_spice=20 if equal_case else 0)
        model.agents[identifier] = agent
        model.occupied[agent.x, agent.y] = identifier
        model.next_id += 1
    model.mean_price = 7
    model.step()
    actual = {'tick': model.tick, 'population': len(model.agents),
              'total_sugar': sum(a.sugar for a in model.agents.values()),
              'total_spice': sum(a.spice for a in model.agents.values()),
              'total_utility': sum(a.wealth for a in model.agents.values()),
              'trade_count': len(model.prices), 'mean_price': model.mean_price}
    for name, value in actual.items():
        assert math.isclose(value, float(row[name]), rel_tol=1e-13, abs_tol=1e-13), (row['case'], name, value, row[name])
    comparisons.append({'case': row['case'], 'independent': actual, 'native': row})
report = {'map_cells': 2500, 'resource_capacities_compared': 5000, 'complete_tick_cases': comparisons,
          'native_hashes': {name: hashlib.sha256((args.native / name).read_bytes()).hexdigest()
                            for name in ['map.csv', 'results.csv']},
          'model_sha256': hashlib.sha256(Path(__file__).with_name('model.py').read_bytes()).hexdigest(),
          'verifier_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
          'limits': 'Controlled full-model tick and map comparison only. No independent ensemble or random-stream equivalence. Equal-MRS potentials are a constructed edge case; frequency in sampled runs is unmeasured.'}
args.output.mkdir(parents=True, exist_ok=False)
(args.output / 'comparison.json').write_text(json.dumps(report, indent=2) + '\n')
print('Matched 5000 resource capacities and all three complete native tick scenarios')
