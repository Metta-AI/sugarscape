"""Audit the declared boundary experiment and summarize complete paired ensembles."""
import argparse
import hashlib
import json
from pathlib import Path
from typing import Literal

import numpy as np
from pydantic import BaseModel, Field
from scipy.stats import t


class Completion(BaseModel):
    scenario: Literal['low-fertility', 'birth-cost']
    seed: int = Field(ge=111, le=120)
    variant: Literal['baseline', 'strict-age', 'strict-wealth', 'strict-both']
    command: list[str]
    exit_code: Literal[0]
    elapsed_seconds: float = Field(gt=0)
    hashes: dict[str, str]


parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('run', type=Path)
parser.add_argument('mode', choices=['prefix', 'complete'])
parser.add_argument('output', type=Path)
args = parser.parse_args()
assert not args.output.exists()
manifest_bytes = (args.run / 'manifest.json').read_bytes()
manifest = json.loads(manifest_bytes)
assert manifest['source_sha256'] == '17803df8b61cfded16718e4895cf574cae77aa514e57a79f99413d7173d49fbc'
assert manifest['seeds'] == list(range(111, 121))
assert (manifest['cycles'], manifest['record_every'], manifest['required_runs']) == (100000, 100, 80)
variants = ['baseline', 'strict-age', 'strict-wealth', 'strict-both']
assert list(manifest['variants']) == variants
baseline = (args.run / 'baseline.cpp').read_bytes()
assert hashlib.sha256(baseline).hexdigest() == manifest['source_sha256']
for variant in variants:
    expected = baseline
    if variant in ['strict-age', 'strict-both']:
        expected = expected.replace(b'agent.age >= 1', b'agent.age > 1')
    if variant in ['strict-wealth', 'strict-both']:
        expected = expected.replace(b'agent.wealth >= birth_cost', b'agent.wealth > birth_cost')
    assert (args.run / (variant + '.cpp')).read_bytes() == expected
    assert hashlib.sha256(expected).hexdigest() == manifest['variants'][variant]['source_sha256']
    assert hashlib.sha256((args.run / variant).read_bytes()).hexdigest() == manifest['variants'][variant]['binary_sha256']
ledger = (args.run / 'completed.jsonl').read_bytes()
records = [Completion.model_validate_json(line) for line in ledger.splitlines()]
expected_order = [(scenario, seed, variant) for scenario in ['low-fertility', 'birth-cost']
                  for seed in range(111, 121) for variant in variants]
assert [(r.scenario, r.seed, r.variant) for r in records] == expected_order[:len(records)]
assert 0 < len(records) <= 80
if args.mode == 'complete':
    assert len(records) == 80, 'All 80 declared runs are required'
    assert json.loads((args.run / 'complete.json').read_text()) == {'completed_runs': 80}
metrics = ['population', 'wealth', 'mean_age', 'gini']
columns = ('cycle', *metrics, 'landscape', 'births', 'deaths', 'growth', 'metabolism', 'death_loss', 'birth_loss', 'conservation_error')
per_run, extinct, identities = [], [], []
for record in records:
    stem = f'{record.scenario}-{record.seed}-{record.variant}'
    aggregate = args.run / (stem + '.csv')
    observations = args.run / (stem + '-observations.csv')
    assert set(record.hashes) == {aggregate.name, observations.name}
    for path in [aggregate, observations]:
        assert hashlib.sha256(path.read_bytes()).hexdigest() == record.hashes[path.name]
    parameters = ['85', '0'] if record.scenario == 'low-fertility' else ['10', '40']
    assert record.command == [str(args.run / record.variant), str(record.seed), *parameters,
                              '100000', '100', str(observations)]
    assert (args.run / (stem + '.stderr')).read_bytes() == b''
    data = np.atleast_1d(np.genfromtxt(aggregate, delimiter=',', names=True))
    assert data.dtype.names == columns
    assert all(np.isfinite(data[c]).all() for c in columns)
    final = int(data['cycle'][-1])
    assert 1 <= final <= 100000
    np.testing.assert_array_equal(data['cycle'], sorted({1, final, *range(100, final + 1, 100)}))
    for column in columns:
        assert (data[column] >= 0).all()
        if column not in ['mean_age', 'gini']:
            np.testing.assert_array_equal(data[column], np.floor(data[column]))
    assert (data['population'] <= 2500).all() and (data['landscape'] <= 10000).all()
    assert (data['gini'] <= 1).all() and (data['mean_age'] <= data['cycle']).all()
    assert (data['conservation_error'] == 0).all()
    np.testing.assert_array_equal(data['birth_loss'], data['births'] * int(parameters[1]))
    # These counters are per-cycle, not cumulative: sparse samples cannot independently
    # reconstruct every population transition. The pinned native binary checks each cycle.
    np.testing.assert_array_equal(data['metabolism'], (data['population'] - data['births']) * 3)
    assert final == 100000 or data['population'][-1] == 0
    item = {'scenario': record.scenario, 'seed': record.seed, 'variant': record.variant,
            'observations': len(data), 'final_cycle': final, 'extinct': bool(data['population'][-1] == 0)}
    if item['extinct']:
        extinct.append(stem)
    else:
        item['windows'] = {}
        for label, start, stop in [('earlier', 50000, 75000), ('later', 75000, 100000)]:
            selected = (data['cycle'] > start) & (data['cycle'] <= stop)
            assert selected.sum() == 250
            item['windows'][label] = {metric: float(data[metric][selected].mean()) for metric in metrics}
    per_run.append(item)
    if record.scenario == 'birth-cost' and record.variant in ['strict-age', 'strict-both']:
        other = 'baseline' if record.variant == 'strict-age' else 'strict-wealth'
        for suffix in ['.csv', '-observations.csv']:
            original = args.run / f'birth-cost-{record.seed}-{other}{suffix}'
            assert original.read_bytes() == (args.run / (stem + suffix)).read_bytes(), 'Age-only invariance failed'
        identities.append({'seed': record.seed, 'variants': [other, record.variant], 'byte_identical_files': 2})
statistics = []
if len(records) == 80 and not extinct:
    critical = float(t.ppf(.975, 9))
    for scenario in ['low-fertility', 'birth-cost']:
        for window in ['earlier', 'later']:
            for metric in metrics:
                values = {variant: np.array([row['windows'][window][metric] for row in per_run
                          if row['scenario'] == scenario and row['variant'] == variant]) for variant in variants}
                contrasts = {**values, 'age_effect_inclusive_wealth': values['strict-age'] - values['baseline'],
                             'age_effect_strict_wealth': values['strict-both'] - values['strict-wealth'],
                             'wealth_effect_inclusive_age': values['strict-wealth'] - values['baseline'],
                             'wealth_effect_strict_age': values['strict-both'] - values['strict-age']}
                for name, sample in contrasts.items():
                    assert len(sample) == 10
                    mean = float(sample.mean())
                    half = critical * float(sample.std(ddof=1)) / np.sqrt(10)
                    statistics.append({'scenario': scenario, 'window': window, 'metric': metric, 'quantity': name,
                                       'mean': mean, 'seed_level_ci95': [mean - half, mean + half]})
report = {'mode': args.mode, 'completed_ensemble': len(records) == 80, 'validated_runs': len(records),
          'required_runs': 80, 'manifest_sha256': hashlib.sha256(manifest_bytes).hexdigest(),
          'ledger_sha256': hashlib.sha256(ledger).hexdigest(),
          'analyzer_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
          'per_run': per_run, 'extinct': extinct, 'age_only_identity_checks': identities, 'statistics': statistics,
          'scope': 'Independent source-variant, file-hash, scalar, timestamp, sampled accounting, and whole-trajectory age-invariance checks. Native every-cycle conservation is enforced by the pinned simulator. Observation hashes are checked but founder/elite semantics are not independently reaudited here. No historical equivalence or paper verdict. Aggregates require all 80 runs and no extinctions; failed societies are never silently excluded.'}
args.output.mkdir(parents=True, exist_ok=False)
(args.output / 'ledger-snapshot.jsonl').write_bytes(ledger)
(args.output / 'analysis.json').write_text(json.dumps(report, indent=2, allow_nan=False) + '\n')
print(f'Validated {len(records)}/80 runs; {len(extinct)} extinctions; {len(identities)} age-only identity pairs')
