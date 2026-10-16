"""Audit individual-seed mortality dominance across every reported robustness dimension."""
import argparse
import hashlib
import itertools
import json
from pathlib import Path

import pandas as pd

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('canonical', type=Path)
parser.add_argument('robustness', type=Path)
parser.add_argument('output', type=Path)
args = parser.parse_args()
assert json.loads((args.canonical / 'exit.json').read_text())['exit_code'] == 0
completed = [json.loads(line) for line in (args.robustness / 'completed.jsonl').read_text().splitlines()]
assert len(completed) == 4 and all(item['exit_code'] == 0 for item in completed)
cells = ['baseline', 'labour/ubi', 'labour/means_tested', 'wealth/ubi', 'wealth/means_tested', 'disp_levy/means_tested', 'uhi_scenario']
sensitivity_cells = ['baseline', 'labour/means_tested', 'wealth/means_tested', 'disp_levy/means_tested', 'uhi_scenario']
pure = ['labour/means_tested', 'wealth/means_tested']
speeds = ['slow', 'balanced', 'fast']
records = []
inputs = []
for name, path, dimensions, allowed_cells, metric in [
    ('canonical', args.canonical / 'results/canonical/part_b_stage5_main.csv', {'km_label': speeds}, cells, 'starvation_deaths_total'),
    ('welfare', args.canonical / 'results/canonical/part_c_welfare_sensitivity.csv', {'km_label': speeds}, sensitivity_cells, 'starvation_deaths_total'),
    ('composition', args.robustness / 'results/canonical/composition_sweep.csv', {'composition': ['low', 'high'], 'km_label': speeds}, cells, 'starvation_deaths_total'),
    ('perseed', args.robustness / 'results/stage5_perseed_thresholds.csv', {'km_label': speeds}, cells, 'starvation_deaths_total'),
    ('horizon', args.robustness / 'results/canonical/horizon_sweep.csv', {'km_label': speeds}, ['baseline', *pure], 'deaths_600'),
]:
    frame = pd.read_csv(path)
    keys = [*dimensions, 'cell_label', 'seed']
    expected = set(itertools.product(*dimensions.values(), allowed_cells, range(5)))
    assert len(frame) == len(expected) and not frame.duplicated(keys).any()
    assert set(frame[keys].itertuples(index=False, name=None)) == expected
    assert frame[metric].notna().all() and frame[metric].ge(0).all()
    assert frame[metric].eq(frame[metric].astype(int)).all()
    inputs.append({'study': name, 'path': str(path), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest(), 'runs': len(frame)})
    for group_key, group in frame.groupby([*dimensions, 'seed']):
        values = group.set_index('cell_label')[metric]
        condition = dict(zip(dimensions, group_key[:-1]))
        condition['seed'] = int(group_key[-1])
        for policy in pure:
            for comparator in [cell for cell in ['baseline', 'labour/ubi', 'wealth/ubi', 'uhi_scenario'] if cell in allowed_cells]:
                left, right = int(values[policy]), int(values[comparator])
                records.append({'study': name, **condition, 'policy': policy, 'comparator': comparator,
                                'policy_deaths': left, 'comparator_deaths': right, 'strictly_lower': left < right,
                                'tie': left == right})
failures = [row for row in records if not row['strictly_lower']]
report = {'inputs': inputs, 'comparisons': records, 'total_comparisons': len(records),
          'strict_dominance_count': sum(row['strictly_lower'] for row in records), 'non_strict_cases': failures,
          'scope': 'Published seeds and available policy arms only. Horizon has no universal-transfer arms; no inference beyond this design or statistical significance claim.'}
args.output.mkdir(parents=True, exist_ok=False)
(args.output / 'mortality-dominance.json').write_text(json.dumps(report, indent=2, allow_nan=False)+'\n')
print(json.dumps({'comparisons': len(records), 'strict_dominance_count': report['strict_dominance_count'], 'non_strict_cases': failures}))
