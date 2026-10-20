"""Check Section 4.2 population and owner-excluded inequality claims from fresh agents."""
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
assert audit['provenance'] == 'fresh-replay'
assert audit['runs'] == 105 and all(row['matches'] for row in audit['table_comparison'])
assert hashlib.sha256(args.snapshot.read_bytes()).hexdigest() == audit['snapshot_sha256']
snapshot = pd.read_csv(args.snapshot)
keys = ['km_label', 'cell_label', 'seed']
rows = []
for key, group in snapshot.groupby(keys):
    on_grid = group[group.AgentType != 'OwnerHumanAgent']
    wealth = on_grid.Wealth.to_numpy(dtype=float)
    assert len(wealth) > 0 and wealth.sum() > 0
    gini = np.abs(wealth[:, None] - wealth[None, :]).sum() / (2 * len(wealth) * wealth.sum())
    rows.append(dict(zip(keys, (key[0], key[1], int(key[2]))), on_grid_population=len(on_grid), owners=len(group)-len(on_grid),
                     total_population=len(group), on_grid_gini=float(gini)))
assert len(rows) == 105
frame = pd.DataFrame(rows)
means = frame.groupby(keys[:2]).on_grid_gini.mean().unstack('km_label')
ranks = means.rank(axis=0, method='min', ascending=True)
comparisons = []
for cell in ['labour/means_tested', 'wealth/means_tested']:
    comparisons.append({'cell': cell, 'slow_mean': float(means.loc[cell, 'slow']),
                        'fast_mean': float(means.loc[cell, 'fast']),
                        'slow_rank': float(ranks.loc[cell, 'slow']),
                        'fast_rank': float(ranks.loc[cell, 'fast']),
                        'rank_increases': bool(ranks.loc[cell, 'fast'] > ranks.loc[cell, 'slow'])})
counts = {speed: {column: sorted(map(int, group[column].unique()))
                 for column in ['on_grid_population', 'owners', 'total_population']}
          for speed, group in frame.groupby('km_label')}
report = {'provenance': 'fresh-replay', 'snapshot_sha256': audit['snapshot_sha256'],
          'decomposition_audit_sha256': hashlib.sha256(args.decomposition_audit.read_bytes()).hexdigest(),
          'method': 'Direct pairwise Gini after excluding OwnerHumanAgent; ranks compare all seven five-seed policy means.',
          'per_run': rows, 'population_counts': counts, 'pure_means_tested_comparisons': comparisons,
          'all_policy_means': means.to_dict(), 'all_policy_ranks': ranks.to_dict(),
          'scope': 'Descriptive owner-exclusion and terminal population checks. No causal identification of spatial competition.'}
args.output.mkdir(parents=True, exist_ok=False)
(args.output / 'owner-exclusion.json').write_text(json.dumps(report, indent=2, allow_nan=False)+'\n')
print(json.dumps({'population_counts': counts, 'comparisons': comparisons}))
