"""Compare five complete native resource/starvation trajectories with the independent model."""
import argparse
import csv
import hashlib
import json
import math
from pathlib import Path

from model import Agent, Model, Parameters, utility

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('native', type=Path)
parser.add_argument('output', type=Path)
args = parser.parse_args()
assert not args.output.exists()
cases = [(1, 1, 0, 4, 4), (3, 3, 0, 4, 4), (1, 1, 0, 4, 0), (1, 1, -1, 4, 4), (1, 1, 6, 4, 4)]
reports = []
for index, (sm, pm, vision, sugar, spice) in enumerate(cases):
    model = Model(Parameters(population=0, mutation=0, maximum_sugar=10, maximum_spice=10, reproduction=100000, seed=123))
    for cell in model.cells:
        model.capacity_sugar[cell] = model.capacity_spice[cell] = model.sugar[cell] = model.spice[cell] = 0
    model.capacity_sugar[25, 25] = model.sugar[25, 25] = sugar
    model.capacity_spice[25, 25] = model.spice[25, 25] = spice
    agent = Agent(identifier=0, x=25, y=25, sugar=10, spice=10, sugar_metabolism=sm,
                  spice_metabolism=pm, vision=vision, wealth=utility(10, 10, sm, pm))
    model.agents[0] = agent
    model.occupied[25, 25] = 0
    model.next_id = 1
    model.mean_price = 7
    path = args.native / f'case-{index}.csv'
    with path.open() as stream:
        reader = csv.reader(stream)
        header = next(reader)
        native = [[float(v) for v in row] for row in reader]
    assert header == ['tick', 'population', 'gini', 'landscape_sugar', 'landscape_spice', 'trades', 'mean_price', 'agent_sugar', 'agent_spice', 'utility']
    assert len(native) == 501 and all(len(row) == 10 for row in native)
    maximum_error = 0.0
    for observation, row in enumerate(native):
        actual = model.observation() + [sum(a.sugar for a in model.agents.values()),
                                       sum(a.spice for a in model.agents.values()), sum(a.wealth for a in model.agents.values())]
        for name, expected, value in zip(header, row, actual):
            assert math.isfinite(expected) and math.isfinite(value)
            assert math.isclose(expected, value, rel_tol=1e-13, abs_tol=1e-13), (index, observation, name, expected, value)
            maximum_error = max(maximum_error, abs(expected - value))
        model.step()
    reports.append({'case': index, 'configuration': {'sugar_metabolism': sm, 'spice_metabolism': pm,
                    'vision': vision, 'patch_sugar_capacity': sugar, 'patch_spice_capacity': spice},
                    'observations': 501, 'compared_values': 5010, 'final_tick': native[-1][0],
                    'final_population': native[-1][1], 'maximum_absolute_error': maximum_error,
                    'native_sha256': hashlib.sha256(path.read_bytes()).hexdigest()})
report = {'cases': reports, 'total_compared_values': 25050,
          'source_sha256': {name: hashlib.sha256(Path(__file__).with_name(name).read_bytes()).hexdigest()
                            for name in ['model.py', 'verify_trajectories.py']},
          'scope': 'Complete deterministic 501-observation trajectories covering regrowth, metabolism, resource-specific starvation, zero/negative/positive vision, and frozen extinction. Not stochastic ensemble equivalence.'}
args.output.mkdir(parents=True, exist_ok=False)
(args.output / 'comparison.json').write_text(json.dumps(report, indent=2) + '\n')
print('Matched 25050 native values across five complete trajectories')
