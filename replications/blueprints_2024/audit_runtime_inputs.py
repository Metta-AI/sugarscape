"""Compare deposited runtime configurations with the homogeneous seed schedule."""
import argparse
import hashlib
import json
from pathlib import Path
import zipfile

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('archives', type=Path)
parser.add_argument('output', type=Path)
args = parser.parse_args()
pins = {'blueprints-homogeneous.zip': '319c38c77cdeb9f3bd618ce6c57e14e93c35e2be282c01332d42cff58327f525',
        'blueprints-runtimes.zip': '43b1967e9af9d7aac9785258706fd5abec6257235940b85aa811519c0e6ae98a'}
archives = {}
for name, digest in pins.items():
    path = args.archives / name
    assert hashlib.sha256(path.read_bytes()).hexdigest() == digest
    with zipfile.ZipFile(path) as archive:
        archives[name] = {entry: json.loads(archive.read(entry)) for entry in archive.namelist()}
homogeneous = archives['blueprints-homogeneous.zip']
runtime = archives['blueprints-runtimes.zip']
assert len(homogeneous) == 2000 and len(runtime) == 1200
original_seeds = {config['seed'] for config in homogeneous.values()}
assert len(original_seeds) == 500
models = sorted({config['agentDecisionModels'][0] for config in homogeneous.values()})
rows = []
for model in models:
    groups = {steps: {config['seed']: config for config in runtime.values()
                     if config['agentDecisionModels'] == [model] and config['timesteps'] == steps}
              for steps in [500, 5000, 50000]}
    assert all(len(group) == 100 for group in groups.values())
    assert groups[500].keys() == groups[5000].keys() == groups[50000].keys()
    seeds = sorted(groups[500])
    for seed in seeds:
        normalized = [{key: value for key, value in groups[steps][seed].items()
                       if key not in {'timesteps', 'logfile'}} for steps in groups]
        assert normalized[0] == normalized[1] == normalized[2]
    rows.append({'model': model, 'seeds': seeds, 'seeds_per_horizon': 100,
                 'homogeneous_seed_overlap': sorted(original_seeds.intersection(seeds)),
                 'horizons': [500, 5000, 50000],
                 'only_cross_horizon_differences': ['timesteps', 'logfile']})
assert all(row['seeds'] == rows[0]['seeds'] for row in rows)
report = {'archives_sha256': pins, 'homogeneous_seeds': 500, 'runtime_configurations': 1200,
          'models': rows, 'paper_table6_seeds_per_model_per_horizon': 500,
          'scope': 'Archive input comparison only; no simulations or negative replication. Runtime archive has 100 shared seeds, none in the homogeneous archive. Paper page19 describes the same500seeds, and each Table6 cell group totals500. Do not substitute this archive for the claimed500seed experiment.'}
args.output.parent.mkdir(parents=True, exist_ok=True)
with args.output.open('x') as stream:
    stream.write(json.dumps(report, indent=2) + '\n')
print(json.dumps({'runtime_configs': 1200, 'runtime_seeds': 100,
                  'homogeneous_seed_overlap': len(rows[0]['homogeneous_seed_overlap'])}))
