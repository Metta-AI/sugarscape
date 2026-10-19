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
assert hashlib.sha256(encoded).hexdigest() == '4ec231b3714289deeab9e92bae99efb3fe4c0cb2552e6ba2e7fd2565a12bc8fd'
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
exclusion_path = Path(__file__).with_name('paper-target-exclusions.json')
exclusions = json.loads(exclusion_path.read_text())
inventory = json.loads(Path(__file__).with_name('figure-panel-inventory.json').read_text())
assert exclusions['paper_sha256'] == inventory['paper_sha256']
for exclusion in exclusions['panels']:
    panels = next(f['panels'] for f in inventory['figures'] if f['figure'] == exclusion['figure'])
    assert sum(p['sha256'] == exclusion['panel_sha256'] and p['group_A'] == exclusion['group_A']
               and p['group_B'] == exclusion['group_B'] for p in panels) == 1
comparisons = []
for figure in curves['figures']:
    records = [r for r in figure['records'] if
               (r['group_A'], r['group_B']) == (summary['group_A'], summary['group_B'])]
    assert len(records) == 2 * (figure['x_calibration']['right_column'] - figure['x_calibration']['left_column'] + 1)
    for record in records:
        field = metrics[figure['figure']][['A', 'B'].index(record['breed'])]
        item = {'figure': figure['figure'], 'metric': field, **record}
        excluded = [e for e in exclusions['panels'] if e['figure'] == figure['figure']
                    and e['panel_sha256'] == record['panel_sha256']]
        assert len(excluded) <= 1
        if excluded:
            item['raster_status'] = item['status']
            item['status'] = excluded[0]['status']
            item['target_exclusion_reason'] = excluded[0]['reason']
        elif 'metric_interval' in record:
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
assert len(comparisons) == 3876
report = {'group_A': summary['group_A'], 'group_B': summary['group_B'],
          'interpretation': summary['interpretation'], 'runs': 50,
          'summary_sha256': hashlib.sha256(summary_path.read_bytes()).hexdigest(),
          'means_sha256': hashlib.sha256((args.cohort / 'means.csv').read_bytes()).hexdigest(),
          'paper_target_exclusions_sha256': hashlib.sha256(exclusion_path.read_bytes()).hexdigest(),
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
