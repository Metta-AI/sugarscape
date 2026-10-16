"""Compare Figure 2's labelled founder with all audited original ensemble seeds."""
import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('run', type=Path)
parser.add_argument('audit', type=Path)
parser.add_argument('output', type=Path)
args = parser.parse_args()
root = Path(__file__).resolve().parent
manifest = (args.run / 'manifest.json').read_bytes()
audit_bytes = (args.audit / 'audit.json').read_bytes()
audit = json.loads(audit_bytes)
assert audit['completed_ensemble'] and audit['validated_runs'] == 200
assert audit['manifest_sha256'] == hashlib.sha256(manifest).hexdigest()
ledger = (args.audit / 'ledger-snapshot.jsonl').read_bytes()
assert hashlib.sha256(ledger).hexdigest() == audit['ledger_snapshot_sha256']
records = [json.loads(line) for line in ledger.splitlines()]
figure = root / 'results/figure2-vector-2026-10-16'
extraction = json.loads((figure / 'extraction.json').read_text())
tables, lifetimes, summaries = [], [], []
for scenario in ['low-fertility', 'birth-cost']:
    selected = [row for row in records if row['scenario'] == scenario]
    assert [row['seed'] for row in selected] == list(range(1, 101))
    provenance = next(row for row in extraction['curves']
                      if row['scenario'] == scenario and row['label'] == 'founder-0')
    source = figure / provenance['filename']
    assert hashlib.sha256(source.read_bytes()).hexdigest() == provenance['gzip_sha256']
    vertices = pd.read_csv(source)
    curve = vertices.groupby('approximate_cycle', sort=True).approximate_wealth.mean()
    # Compare only observed native times inside the published path; no extrapolation.
    cycles = np.arange(100, int(curve.index.max()) + 1, 100)
    assert curve.index.min() <= cycles.min()
    published = np.interp(cycles, curve.index, curve.to_numpy())
    matrix = np.full((100, len(cycles)), np.nan)
    for index, record in enumerate(selected):
        name = f"{scenario}-{record['seed']}-observations.csv"
        raw = (args.run / name).read_bytes()
        assert hashlib.sha256(raw).hexdigest() == record['raw_sha256'][name]
        observations = pd.read_csv(args.run / name)
        founder = observations[(observations.kind == 'founder') & (observations.agent_id == 0)].set_index('cycle')
        assert founder.index.is_unique and founder.index.is_monotonic_increasing
        assert (founder.mean_age == founder.index).all()
        assert (founder.wealth >= 0).all()
        matrix[index] = founder.wealth.reindex(cycles).to_numpy()
        last = int(founder.index.max())
        lifetimes.append({'scenario': scenario, 'seed': record['seed'], 'last_observed_alive': last,
                          'first_observed_absent': last + 100 if last < 50000 else None,
                          'right_censored_at_horizon': last == 50000})
    alive = np.isfinite(matrix).sum(axis=0)
    # Dead agents contribute to survival counts, never fictitious zero wealth.
    assert (alive > 0).all(), 'No survivor wealth distribution at one or more published times'
    low, median, high = np.nanquantile(matrix, [.025, .5, .975], axis=0)
    table = pd.DataFrame({'scenario': scenario, 'cycle': cycles, 'published_approximate_wealth': published,
                         'founders_alive_of_100': alive, 'survivor_wealth_q025': low,
                         'survivor_wealth_median': median, 'survivor_wealth_q975': high})
    tables.append(table)
    scenario_lifetimes = [row for row in lifetimes if row['scenario'] == scenario]
    summaries.append({'scenario': scenario, 'seeds': 100, 'shared_cycles': len(cycles),
                      'published_last_path_cycle': float(curve.index.max()),
                      'last_shared_cycle': int(cycles[-1]), 'survivors_at_last_shared_cycle': int(alive[-1]),
                      'right_censored_founders_at_50000': sum(row['right_censored_at_horizon'] for row in scenario_lifetimes),
                      'last_observed_alive_quantiles_025_50_975': np.quantile(
                          [row['last_observed_alive'] for row in scenario_lifetimes], [.025, .5, .975]).tolist(),
                      'published_fraction_inside_survivor_wealth_pointwise_95_percent_interval':
                          float(((published >= low) & (published <= high)).mean()),
                      'source_csv_gzip_sha256': provenance['gzip_sha256']})
report = {'summaries': summaries, 'audit_sha256': hashlib.sha256(audit_bytes).hexdigest(),
          'comparison_source_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
          'limits': 'Descriptive comparison, not an acceptance test. Published seed is unknown. Only explicitly labelled founder zero is matched. Grey paths have no verified agent IDs. Vector coordinates are approximate; path endpoints are not exact death records. Native deaths are interval-censored by 100-cycle recording. Wealth quantiles condition on survival and are pointwise seed intervals, not confidence or simultaneous intervals. No historical model equivalence is established.'}
args.output.mkdir(parents=True, exist_ok=False)
pd.concat(tables).to_csv(args.output / 'comparison.csv', index=False)
pd.DataFrame(lifetimes).to_csv(args.output / 'founder-lifetimes.csv', index=False)
(args.output / 'comparison.json').write_text(json.dumps(report, indent=2, allow_nan=False) + '\n')
print(json.dumps(summaries, indent=2))
