"""Describe complete-cohort agreement with visible paper curves, without a statistical verdict."""

import argparse
import csv
import gzip
import hashlib
import json
import math
from pathlib import Path

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('cohort', type=Path)
parser.add_argument('curves', type=Path)
parser.add_argument('new_output', type=Path)
args = parser.parse_args()
summary_path = args.cohort / 'summary.json'
summary = json.loads(summary_path.read_text())
assert summary['runs'] == 50 and summary['observations'] == 1000050
assert len(summary['trajectory_sha256']) == 50
encoded = args.curves.read_bytes()
assert hashlib.sha256(encoded).hexdigest() == 'aa946661747421eb83134a2cf9ca91a09b0150e563729e8df09696e7320615df'
curves = json.loads(gzip.decompress(encoded))
with (args.cohort / 'means.csv').open() as file:
    means = list(csv.DictReader(file))
assert len(means) == 20001
assert all(int(row['tick']) == tick for tick, row in enumerate(means))
metrics = {
    3: ['mean [sugar] of group-A', 'mean [sugar] of group-B'],
    4: ['mean [vision] of group-A', 'mean [vision] of group-B'],
    5: ['mean [metabolism] of group-A', 'mean [metabolism] of group-B'],
    6: ['combat-agent-a-die', 'combat-agent-b-die'],
    7: ['starve-agent-a-die', 'starve-agent-b-die'],
    8: ['mean [age] of group-A', 'mean [age] of group-B'],
    9: ['max [age] of group-A', 'max [age] of group-B'],
}
comparisons = []
for figure in curves['figures']:
    records = [r for r in figure['records'] if
               (r['group_A'], r['group_B']) == (summary['group_A'], summary['group_B'])]
    assert len(records) == 572
    for record in records:
        field = metrics[figure['figure']][['A', 'B'].index(record['breed'])]
        item = {'figure': figure['figure'], 'metric': field, **record}
        if 'metric_interval' in record:
            lo, hi = record['approximate_tick_interval']
            assert 0 <= lo <= hi <= 20000
            values = [float(means[t][field]) for t in range(math.ceil(lo), math.floor(hi) + 1)]
            # Include fractional endpoints of the piecewise-linear mean curve.
            for tick in (lo, hi):
                left, right = math.floor(tick), math.ceil(tick)
                values.append(float(means[left][field]) * (right - tick)
                              + float(means[right][field]) * (tick - left)
                              if left != right else float(means[left][field]))
            assert all(math.isfinite(v) for v in values)
            model_lo, model_hi = min(values), max(values)
            paper_lo, paper_hi = record['metric_interval']
            item['cohort_mean_range_over_tick_interval'] = [model_lo, model_hi]
            item['signed_range_separation'] = (model_lo - paper_hi if model_lo > paper_hi else
                                               model_hi - paper_lo if model_hi < paper_lo else 0)
        comparisons.append(item)
assert len(comparisons) == 4004
report = {'group_A': summary['group_A'], 'group_B': summary['group_B'],
          'interpretation': summary['interpretation'], 'runs': 50,
          'summary_sha256': hashlib.sha256(summary_path.read_bytes()).hexdigest(),
          'means_sha256': hashlib.sha256((args.cohort / 'means.csv').read_bytes()).hexdigest(),
          'curves_sha256': hashlib.sha256(encoded).hexdigest(),
          'records': comparisons,
          'limits': ['Descriptive range separation only; zero does not establish equivalence.',
                     'Raster bounds and horizontal calibration margins are not sampling confidence intervals.',
                     'Paper seeds and between-run uncertainty are unavailable.',
                     'Adjacent raster columns are dependent; no binomial test or significance claim is valid.',
                     'Unresolved paper curves stay unresolved; no interpolation through occluded paper segments.',
                     'Independent cohort arithmetic verification remains a separate required check.']}
args.new_output.mkdir()
(args.new_output / 'curve-comparison.json.gz').write_bytes(
    gzip.compress((json.dumps(report, separators=(',', ':')) + '\n').encode(), mtime=0))
print(json.dumps({'records': len(comparisons),
                  'visible': sum('signed_range_separation' in r for r in comparisons),
                  'scope': 'Descriptive comparison only; no replication verdict.'}))
