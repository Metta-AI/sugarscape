from pathlib import Path
import csv
import gzip
import hashlib
import io
import json

import numpy as np

root = Path(__file__).resolve().parent
repo = Path('/Users/relh/Code/workspace/sugarscape-brearcliffe/replications/brearcliffe_2020')
protocol = json.loads((root / 'protocol.json').read_bytes())
audit_path = root.parent / 'brearcliffe-paper-rule-m-q-snapshot-001/union-audit/audit.json'
audit = json.loads(audit_path.read_bytes())
lookup = {row['run_id']: row for row in audit['completed']}
assert len(lookup) == 852
cohorts = ['rule-m-ec', 'rule-m-q', 'rule-m-sarsa', 'ec-rule-m', 'q-rule-m', 'sarsa-rule-m']
records = []
pins = {}
endpoint_rows = []
source_files = {}
for pair, name in zip(protocol['pair_indices'], cohorts, strict=True):
    folder = repo / 'results' / (name + '-complete-cohort-2026-10-19')
    summary = json.loads((folder / 'cohort-summary.json').read_bytes())
    assert summary['pair_index'] == pair and summary['interpretation'] == 'released-code'
    assert summary['runs'] == 50
    side = 'A' if summary['group_A'] == 'Rule M' else 'B'
    other = 'B' if side == 'A' else 'A'
    assert summary['group_' + side] == 'Rule M' and summary['group_' + other] != 'Rule M'
    fields = [f'mean [{metric}] of group-{breed}' for metric in protocol['metrics'] for breed in [side, other]]
    endpoints = []
    for repeat in range(50):
        run_id = f'released-code-pair-{pair:02d}-repeat-{repeat:02d}'
        row = lookup[run_id]
        raw = (Path(row['directory']) / 'trajectory.csv').read_bytes()
        digest = hashlib.sha256(raw).hexdigest()
        assert digest == row['trajectory_sha256'] == summary['trajectory_sha256'][run_id]
        lines = raw.splitlines()
        assert len(lines) == 20002
        end = next(csv.DictReader(io.StringIO((lines[0] + b'\n' + lines[-1] + b'\n').decode())))
        assert int(end['tick']) == 20000
        values = [float(end[field]) for field in fields]
        assert np.isfinite(values).all()
        endpoints.append(values)
        endpoint_rows.append([pair, run_id, *values])
        pins[run_id] = digest
    matrix = np.array(endpoints)
    index_raw = gzip.decompress((folder / 'bootstrap-indices.u8.gz').read_bytes())
    assert hashlib.sha256(index_raw).hexdigest() == summary['bootstrap']['indices_sha256']
    indices = np.frombuffer(index_raw, dtype=np.uint8).reshape(20000, 50)
    assert indices.max() < 50
    with gzip.open(folder / 'means.csv.gz', 'rt') as stream:
        means = list(csv.DictReader(stream))
    assert [int(row['tick']) for row in means] == list(range(20001))
    for filename in ['cohort-summary.json', 'bootstrap-indices.u8.gz', 'means.csv.gz']:
        source_files[str(folder / filename)] = hashlib.sha256((folder / filename).read_bytes()).hexdigest()
    for j, metric in enumerate(protocol['metrics']):
        differences = matrix[:, 2*j] - matrix[:, 2*j+1]
        draws = differences[indices].mean(axis=1)
        interval = np.quantile(draws, [.025, .975], method='linear')
        curve = np.array([float(row[fields[2*j]]) - float(row[fields[2*j+1]]) for row in means])
        assert abs(curve[-1] - differences.mean()) <= 1e-12 * max(1, abs(curve[-1]))
        records.append({
            'pair_index': pair, 'pairing': name, 'opponent': summary['group_' + other], 'rule_m_side': side,
            'metric': metric, 'paired_endpoint_mean': float(differences.mean()),
            'paired_endpoint_sample_sd': float(differences.std(ddof=1)),
            'pointwise_bootstrap_interval_95': interval.tolist(),
            'endpoint_positive_runs': int((differences > 0).sum()),
            'endpoint_equal_runs': int((differences == 0).sum()),
            'endpoint_negative_runs': int((differences < 0).sum()),
            'initial_mean_difference': float(curve[0]),
            'post_initial_positive_ticks': int((curve[1:] > 0).sum()),
            'post_initial_equal_ticks': int((curve[1:] == 0).sum()),
            'post_initial_negative_ticks': int((curve[1:] < 0).sum()),
            'minimum_post_initial_difference': float(curve[1:].min()),
            'maximum_post_initial_difference': float(curve[1:].max()),
        })
with (root / 'paired-endpoints.csv').open('w') as stream:
    writer = csv.writer(stream, lineterminator="\n")
    writer.writerow(['pair_index', 'run_id'] + [f'{metric}_{role}' for metric in protocol['metrics'] for role in ['rule_m', 'opponent']])
    writer.writerows(endpoint_rows)
assert len(pins) == 300 and len(records) == 18
report = {'inputs': 300, 'contrasts': 18, 'raw_trajectory_sha256': pins, 'source_files_sha256': source_files,
          'audit_sha256': hashlib.sha256(audit_path.read_bytes()).hexdigest(), 'records': records, 'scope': protocol['scope']}
(root / 'contrasts.json').write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps(records, indent=2))
