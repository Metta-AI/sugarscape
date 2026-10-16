"""Check Section 4.2 within-type interpretation against validated fresh agents."""
import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('snapshot', type=Path)
parser.add_argument('decomposition_audit', type=Path)
parser.add_argument('output', type=Path)
args = parser.parse_args()
audit = json.loads(args.decomposition_audit.read_text())
assert audit['provenance'] == 'fresh-replay' and audit['runs'] == 105
assert all(row['matches'] for row in audit['table_comparison'])
assert hashlib.sha256(args.snapshot.read_bytes()).hexdigest() == audit['snapshot_sha256']
keys = ['km_label', 'cell_label', 'seed']
snapshot = pd.read_csv(args.snapshot)
existing = pd.DataFrame(audit['per_run']).set_index(keys)
rows = []
for key, group in snapshot.groupby(keys):
    denominator = 2 * len(group) * group.Wealth.sum()
    total_within = 0.0
    for agent_type, subgroup in group.groupby('AgentType'):
        wealth = subgroup.Wealth.to_numpy(dtype=float)
        numerator = np.abs(wealth[:, None] - wealth[None, :]).sum()
        contribution = float(numerator / denominator)
        within_gini = float(numerator / (2 * len(wealth) * wealth.sum()))
        rows.append({'km_label': key[0], 'cell_label': key[1], 'seed': int(key[2]),
                     'agent_type': agent_type, 'population': len(wealth),
                     'within_contribution': contribution, 'type_gini': within_gini})
        total_within += contribution
    assert np.isclose(total_within, existing.loc[key, 'within'], rtol=1e-12, atol=1e-12)
assert len(rows) == 420
means = pd.DataFrame(rows).groupby(['km_label', 'cell_label', 'agent_type'])[['within_contribution', 'type_gini']].mean()
checks = []
for speed in ['slow', 'balanced', 'fast']:
    baseline = means.loc[(speed, 'baseline')]
    for cell in ['labour/means_tested', 'wealth/means_tested']:
        policy = means.loc[(speed, cell)]
        b = float(baseline.within_contribution.sum())
        p = float(policy.within_contribution.sum())
        checks.append({'speed': speed, 'policy': cell, 'baseline_within': b, 'policy_within': p,
                       'contribution_lower_than_baseline': p < b,
                       'largest_baseline_type': baseline.within_contribution.idxmax(),
                       'largest_policy_type': policy.within_contribution.idxmax(),
                       'per_type': [{'agent_type': kind, 'baseline_gini': float(baseline.loc[kind, 'type_gini']),
                                     'policy_gini': float(policy.loc[kind, 'type_gini']),
                                     'baseline_contribution': float(baseline.loc[kind, 'within_contribution']),
                                     'policy_contribution': float(policy.loc[kind, 'within_contribution'])}
                                    for kind in baseline.index]})
report = {'provenance': 'fresh-replay', 'snapshot_sha256': audit['snapshot_sha256'],
          'decomposition_audit_sha256': hashlib.sha256(args.decomposition_audit.read_bytes()).hexdigest(),
          'method': 'Direct pairwise differences; weighted contributions use the full population denominator; type Gini uses only the subgroup denominator.',
          'runs': 105, 'per_run_type': rows, 'comparisons': checks,
          'lower_contribution_comparisons': sum(row['contribution_lower_than_baseline'] for row in checks),
          'scope': 'Descriptive inequality accounting, not a causal estimate of the transfer rule.'}
args.output.mkdir(parents=True, exist_ok=False)
(args.output / 'within-type.json').write_text(json.dumps(report, indent=2, allow_nan=False)+'\n')
print(json.dumps({'comparisons': checks, 'lower_contribution_comparisons': report['lower_contribution_comparisons']}))
