"""Link the complete native experiment to published summaries and storage receipts."""
from pathlib import Path
import hashlib
import json
import sys

results, output = map(Path, sys.argv[1:])
assert not output.exists()
pins = {}


def read(name):
    path = results / name
    pins[name] = hashlib.sha256(path.read_bytes()).hexdigest()
    return json.loads(path.read_bytes())


audit = read('paper-sarsa-sarsa-complete-cohort-2026-10-20/audit.json')
assert (audit['completed_inputs'], audit['remaining_inputs'], audit['observations']) == (1600, 0, 32001600)
runs = {row['run_id']: row for row in audit['completed']}
assert len(runs) == 1600
comparison = read('sixteen-pair-parameter-comparison-2026-10-20/parameter-comparison.json')
for name, expected in comparison['source_sha256'].items():
    actual = hashlib.sha256((results / name).read_bytes()).hexdigest()
    assert actual == expected, name
    pins[name] = actual
cohorts = []
seen = set()
for name in comparison['source_sha256']:
    if not name.endswith('/cohort-summary.json'):
        continue
    cohort = read(name)
    directory = str(Path(name).parent)
    verification = read(directory + '/r-validation.json')
    assert cohort['runs'] == verification['runs'] == 50
    assert cohort['observations'] == verification['observations'] == 1000050
    assert verification['summary_sha256'] == pins[name]
    assert verification['means_checked'] == verification['sample_standard_deviations_checked'] == 320016
    assert verification['endpoint_metrics'] == 14
    for run_id, digest in cohort['trajectory_sha256'].items():
        assert run_id not in seen
        assert runs[run_id]['trajectory_sha256'] == digest
        assert runs[run_id]['observations'] == 20001
        seen.add(run_id)
    cohorts.append({'interpretation': cohort['interpretation'], 'pair_index': cohort['pair_index'], 'summary': name})
assert seen == set(runs) and len(cohorts) == 32
assert {(c['interpretation'], c['pair_index']) for c in cohorts} == {(kind, pair) for kind in ['released-code', 'paper-table'] for pair in range(16)}

stored_hashes = set()
for path in sorted(results.glob('*/storage-readback.json')):
    receipt = read(str(path.relative_to(results)))
    if 'manifest_sha256' in receipt:
        name = str(path.parent.relative_to(results) / 'manifest.json')
        manifest = read(name)
        assert pins[name] == receipt['manifest_sha256']
        receipt_archives = {a['sha256'] for a in receipt['archives']}
        for archive in manifest['archives']:
            assert archive['sha256'] in receipt_archives
            stored_hashes.update(value['sha256'] for key, value in archive['files'].items() if key.endswith('/trajectory.csv'))
    else:
        assert receipt['fresh_download_exact'] and receipt['snapshot_run_members_exact']
        stored_hashes.update(value['sha256'] for key, value in receipt['member_sha256'].items() if key.endswith('/trajectory.csv'))
recovery = read('released-sarsa-sarsa-complete-cohort-2026-10-19/archive-readback.json')
stored_hashes.update(value for key, value in recovery['member_sha256'].items() if key.endswith('/trajectory.csv'))
ecq = 'paper-ec-q-complete-cohort-2026-10-19/'
snapshot = read(ecq + 'snapshot.json')
receipt = read(ecq + 'artifacts.json')
assert receipt['complete_export_and_independent_raw_readback']
assert receipt['sha256'] == snapshot['archive_sha256']
assert read(ecq + 'validation.json')['archive_members_verified'] == len(snapshot['files'])
stored_hashes.update(value['sha256'] for key, value in snapshot['files'].items() if key.endswith('/trajectory.csv'))
terminal = 'released-terminal-audited-2026-10-19/'
delta = read(terminal + 'delta-audit.json')
assert delta['completed_inputs'] == 25
terminal_receipt = read(terminal + 'archive-readback.json')
assert terminal_receipt['bytes'] == 471895938
read(terminal + 'storage-object.json')
for row in delta['completed']:
    assert runs[row['run_id']]['trajectory_sha256'] == row['trajectory_sha256']
    stored_hashes.add(row['trajectory_sha256'])
assert all(row['trajectory_sha256'] in stored_hashes for row in runs.values())

parameter_r = read('sixteen-pair-parameter-comparison-2026-10-20/parameter-r-verification.json')
homogeneous = read('paper-homogeneous-claims-2026-10-20/contrasts.json')
assert homogeneous['inputs'] == 200 and homogeneous['contrasts'] == 28
assert all(row['pointwise_bootstrap_interval_95'][0] <= 0 <= row['pointwise_bootstrap_interval_95'][1] for row in homogeneous['records'])
assert read('paper-homogeneous-claims-2026-10-20/r-verification.json')['raw_endpoint_values_checked'] == 2800
trends = read('complete-horizon-trends-2026-10-20/report.json')
assert len(trends['records']) == 80
assert all(row['final_minus_initial'] < 0 for row in trends['records'])
assert read('complete-horizon-trends-2026-10-20/r-decimal-validation.json')['all_step_sign_counts_exact']
for name in ['paper-rule-m-claims-2026-10-20', 'paper-ec-claims-2026-10-20', 'paper-q-sarsa-claims-2026-10-20', 'rule-m-claim-contrasts-2026-10-19', 'ec-claim-contrasts-2026-10-19', 'q-sarsa-claim-contrasts-2026-10-19', 'homogeneous-breed-contrasts-2026-10-19']:
    read(name + '/r-verification.json')
output.write_text(json.dumps({'completed_inputs': len(runs), 'observations': audit['observations'], 'cohorts': cohorts, 'all_native_hashes_linked_to_cohorts': True, 'all_native_hashes_linked_to_prior_verified_storage_evidence': True, 'parameter_independent_r': parameter_r, 'source_sha256': pins, 'scope': 'Final linkage review of completed native workflow, independent arithmetic and prior fresh storage checks; does not rerun simulations or establish historical numerical equivalence.'}, indent=2) + '\n')
