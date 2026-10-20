"""Posthoc complete-horizon descriptive trends; no selected windows or inference."""
from pathlib import Path
import csv
import gzip
import hashlib
import io
import json
import sys

results, comparison_path, output = map(Path, sys.argv[1:4])
assert not output.exists()
comparison = json.loads(comparison_path.read_bytes())
assert len(comparison['pairings']) == 16
summaries = sorted(name for name in comparison['source_sha256'] if name.endswith('/cohort-summary.json'))
assert len(summaries) == 32
records = []
pins = {}
seen = set()
for name in summaries:
    path = results / name
    assert hashlib.sha256(path.read_bytes()).hexdigest() == comparison['source_sha256'][name]
    summary = json.loads(path.read_bytes())
    key = (summary['interpretation'], summary['pair_index'])
    assert key not in seen and summary['runs'] == 50
    seen.add(key)
    means = path.parent / 'means.csv.gz'
    means_name = str(means.relative_to(results))
    assert hashlib.sha256(means.read_bytes()).hexdigest() == comparison['source_sha256'][means_name]
    rows = list(csv.DictReader(io.StringIO(gzip.decompress(means.read_bytes()).decode())))
    assert len(rows) == 20001 and [int(row['tick']) for row in rows] == list(range(20001))
    for breed in ['A', 'B']:
        method = summary[f'group_{breed}']
        for metric in ['metabolism'] + (['vision'] if method == 'EC' else []):
            field = f'mean [{metric}] of group-{breed}'
            values = [float(row[field]) for row in rows]
            delta = [b - a for a, b in zip(values, values[1:])]
            records.append({'interpretation': key[0], 'pair_index': key[1], 'breed': breed, 'method': method, 'metric': metric, 'initial_mean': values[0], 'final_mean': values[-1], 'final_minus_initial': values[-1] - values[0], 'increasing_steps': sum(x > 0 for x in delta), 'decreasing_steps': sum(x < 0 for x in delta), 'unchanged_steps': sum(x == 0 for x in delta), 'source_means': means_name})
    pins[name] = comparison['source_sha256'][name]
    pins[means_name] = comparison['source_sha256'][means_name]
assert seen == {(kind, pair) for kind in ['released-code', 'paper-table'] for pair in range(16)}
assert len(records) == 80
output.mkdir()
with (output / 'trends.csv').open('x') as stream:
    writer = csv.DictWriter(stream, fieldnames=list(records[0]))
    writer.writeheader()
    writer.writerows(records)
(output / 'report.json').write_text(json.dumps({'cohorts': 32, 'records': records, 'source_sha256': pins, 'comparison_sha256': hashlib.sha256(comparison_path.read_bytes()).hexdigest(), 'scope': 'Posthoc descriptive initial-to-final cohort-mean changes and all20000step signs. No selected time window, monotonicity tolerance, uncertainty interval, equivalence or causal attribution. Cohort means already independently checked against raw trajectories.'}, indent=2) + '\n')
