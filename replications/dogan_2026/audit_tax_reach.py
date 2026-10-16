"""Observe the native tax base by agent type without changing model outcomes."""
import argparse
import hashlib
import json
from pathlib import Path
import sys

import numpy as np
import pandas as pd

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('engine', type=Path)
parser.add_argument('canonical', type=Path)
parser.add_argument('output', type=Path)
args = parser.parse_args()
engine = args.engine.resolve()
manifest = json.loads((args.canonical / 'manifest.json').read_text())
assert json.loads((args.canonical / 'exit.json').read_text())['exit_code'] == 0
assert manifest['revision'] == '0b6a3df470388f60535d8ffb67c34a7f9fa0059a'
for name, checksum in manifest['source_sha256'].items():
    assert hashlib.sha256((engine / name).read_bytes()).hexdigest() == checksum
canonical = args.canonical / 'results/canonical/part_b_stage5_main.csv'
assert hashlib.sha256(canonical.read_bytes()).hexdigest() == manifest['reference_sha256']['results/canonical/part_b_stage5_main.csv']
main = pd.read_csv(canonical).set_index(['km_label', 'cell_label', 'seed'])
sys.path.insert(0, str(engine))
from sugarscape_ai_tax.model import SugarscapeAITax

args.output.mkdir(parents=True, exist_ok=False)
calibration = SugarscapeAITax(tax_regime='none', redistribution_mode='none', k=0, m=0, seed=42)
calibration.run_model(200)
calibration_frame = calibration.datacollector.get_model_vars_dataframe()
calibration_frame.to_csv(args.output / 'calibration.csv', index=False)
parameters = {'income_threshold': float(calibration_frame.MedianIncome.iloc[199]),
              'wealth_threshold_lower': 50, 'wealth_threshold_upper': 2 * float(calibration_frame.MedianWealth.iloc[199]),
              'redistribution_mode': 'means_tested', 'k': 5, 'm': 20, 'seed': 0}
code = SugarscapeAITax._collect_tax.__code__
events = []


def trace(frame, event, arg):
    if frame.f_code is not code:
        return None
    if event == 'return':
        agent = frame.f_locals['agent']
        events.append({'step': int(frame.f_locals['self']._current_step),
                       'agent_type': type(agent).__name__, 'tax': float(agent.tax_paid)})
    return trace


reports = []
for regime in ['labour', 'wealth']:
    events.clear()
    for mode in ['native', 'observed']:
        model = SugarscapeAITax(tax_regime=regime, **parameters)
        if mode == 'observed':
            sys.settrace(trace)
        try:
            model.run_model(300)
        finally:
            sys.settrace(None)
        frame = model.datacollector.get_model_vars_dataframe()
        frame.to_csv(args.output / f'{regime}-{mode}.csv', index=False)
        print(f'{regime} {mode} complete', flush=True)
    assert (args.output / f'{regime}-native.csv').read_bytes() == (args.output / f'{regime}-observed.csv').read_bytes()
    expected = main.loc[('fast', regime + '/means_tested', 0)]
    assert np.isclose(frame.Gini.iloc[-1], expected.gini_final, atol=1e-12, rtol=1e-12)
    assert frame.StarvationDeaths.sum() == expected.starvation_deaths_total
    assert np.isclose(frame.TaxRevenue.sum(), expected.total_tax_revenue, atol=1e-9, rtol=1e-12)
    observations = pd.DataFrame(events)
    assert set(observations.step) == set(range(1, 301))
    assert np.isfinite(observations.tax).all() and observations.tax.ge(0).all()
    per_step = observations.groupby('step').tax.sum()
    assert np.allclose(per_step.to_numpy(), frame.TaxRevenue.to_numpy(), atol=1e-9, rtol=1e-12)
    observations.to_csv(args.output / f'{regime}-tax-events.csv', index=False)
    totals = [{'agent_type': kind, 'tax_calls': len(group), 'positive_tax_calls': int(group.tax.gt(0).sum()),
               'total_tax': float(group.tax.sum())} for kind, group in observations.groupby('agent_type')]
    reports.append({'tax_regime': regime, 'native_observed_byte_identical': True,
                    'canonical_gini_mortality_tax_match': True, 'per_step_tax_accounting_matches': True,
                    'tax_by_type': totals})
report = {'parameters': parameters, 'steps': 300, 'source_sha256': manifest['source_sha256'],
          'canonical_sha256': hashlib.sha256(canonical.read_bytes()).hexdigest(), 'runs': reports,
          'scope': 'Full native fast-automation seed-zero trajectories with tax observations; establishes implemented tax reach, not causal policy effectiveness or all-seed tax shares.'}
(args.output / 'tax-reach.json').write_text(json.dumps(report, indent=2, allow_nan=False)+'\n')
print(json.dumps(reports))
