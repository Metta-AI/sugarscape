"""Run a bounded original-input interval through the frozen independent model."""
import argparse
import csv
import gzip
import hashlib
import io
import json
import platform
import shutil
import time
from pathlib import Path

import numpy as np
import pydantic

from model import Model, Parameters

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('parameters', type=Path)
parser.add_argument('reference', type=Path)
parser.add_argument('start', type=int)
parser.add_argument('stop', type=int)
parser.add_argument('output', type=Path)
args = parser.parse_args()
parameter_bytes = args.parameters.read_bytes()
inputs = list(csv.DictReader(io.StringIO(parameter_bytes.decode())))
assert len(inputs) == 5000 and 0 <= args.start < args.stop <= 5000
with args.reference.open() as stream:
    reference_header = next(csv.reader(stream))
assert len(reference_header) == 150
names = ['count turtles', 'normalized-gini', 'sum [psugar] of patches', 'sum [pspice] of patches', 'number_of_prices', 'mean_prices']
args.output.mkdir(parents=True, exist_ok=False)
root = Path(__file__).resolve().parent
manifest = {'start': args.start, 'stop': args.stop, 'required_inputs': 5000, 'observations_each': 501,
            'parameter_sha256': hashlib.sha256(parameter_bytes).hexdigest(),
            'reference_sha256': hashlib.sha256(args.reference.read_bytes()).hexdigest(),
            'source_sha256': {name: hashlib.sha256((root / name).read_bytes()).hexdigest()
                              for name in ['model.py', 'run_independent.py', 'INDEPENDENT_ENSEMBLE.md']},
            'python': platform.python_version(), 'numpy': np.__version__, 'pydantic': pydantic.__version__,
            'scope': 'Independent Python RNG; no exact NetLogo trajectory-equivalence claim.'}
(args.output / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
with (args.output / 'summary_statistics.csv').open('x', newline='') as statistics, (args.output / 'completed.jsonl').open('x') as ledger:
    summary_writer = csv.DictWriter(statistics, fieldnames=reference_header)
    summary_writer.writeheader()
    statistics.flush()
    for index in range(args.start, args.stop):
        assert shutil.disk_usage(args.output).free > 2 * 1024 ** 3, 'Less than 2 GiB free; preserve evidence and stop'
        started = time.monotonic()
        source = inputs[index]
        for name in ['initial-population', 'maximum-sugar-endowment', 'maximum-spice-endowment', 'wealth-reproduction']:
            assert float(source[name]).is_integer()
        parameters = Parameters(population=int(float(source['initial-population'])), mutation=float(source['pmut']),
                                maximum_sugar=int(float(source['maximum-sugar-endowment'])),
                                maximum_spice=int(float(source['maximum-spice-endowment'])),
                                reproduction=float(source['wealth-reproduction']), seed=int(float(source['random-seed'])))
        model = Model(parameters)
        observations = []
        trajectory_path = args.output / f'row-{index}.csv'
        with trajectory_path.open('x', newline='') as trajectory:
            writer = csv.writer(trajectory, lineterminator='\n')
            writer.writerow(['tick', *names])
            for _ in range(501):
                row = model.observation()
                assert all(np.isfinite(value) for value in row)
                assert 0 <= row[1] <= 2500 and -1e-12 <= row[2] <= 1 + 1e-12
                assert 0 <= row[3] <= 10000 and 0 <= row[4] <= 10000 and row[5] >= 0 and row[6] >= 0
                if observations:
                    previous = observations[-1]
                    assert row[0] == previous[0] + (previous[1] > 0)
                    if previous[1] == 0:
                        assert row == previous
                observations.append(row)
                writer.writerow(row)
                model.step()
        measured = {}
        matrix = np.asarray(observations, dtype=float)
        assert matrix.shape == (501, 7)
        for column, name in enumerate(names, 1):
            values = matrix[:, column]
            measured.update({'mean_' + name: float(values.mean()), 'min_' + name: float(values.min()),
                             'last_' + name: float(values[-1]), 'sd_' + name: float(values.std()),
                             'trend_' + name: float(np.polyfit(np.arange(501, dtype=float), values, 1)[0]),
                             'max_' + name: float(values.max())})
            for observation in range(25, 500, 25):
                measured[f'snap_{observation}_{name}'] = float(values[observation])
        assert measured.keys() == set(reference_header)
        raw = trajectory_path.read_bytes()
        packed = gzip.compress(raw, mtime=0)
        assert gzip.decompress(packed) == raw
        (args.output / f'row-{index}.csv.gz').write_bytes(packed)
        summary_writer.writerow(measured)
        statistics.flush()
        record = {'row': index, 'parameters': parameters.model_dump(), 'archived_seed': source['random-seed'],
                  'observations': 501, 'last_tick': observations[-1][0], 'last_population': observations[-1][1],
                  'trajectory_sha256': hashlib.sha256(raw).hexdigest(), 'gzip_sha256': hashlib.sha256(packed).hexdigest(),
                  'elapsed_seconds': time.monotonic() - started}
        ledger.write(json.dumps(record, allow_nan=False) + '\n')
        ledger.flush()
        print(f'Completed input {index}', flush=True)
(args.output / 'complete.json').write_text(json.dumps({'start': args.start, 'stop': args.stop, 'completed_inputs': args.stop - args.start}) + '\n')
