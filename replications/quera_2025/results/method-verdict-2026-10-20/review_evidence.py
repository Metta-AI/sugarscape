"""Check the complete retained study's evidence links, counts and archive manifests."""
from pathlib import Path
import gzip
import hashlib
import json
import sys

results = Path(sys.argv[1])
output = Path(sys.argv[2])
assert not output.exists()
pins = {}
optimizer_components = 0
validation_draws = 0
for method in ['pathwise', 'vargrad']:
    folder = results / f'{method}-full-calibration-2026-10-20'
    audit_bytes = gzip.decompress((folder / 'audit.json.gz').read_bytes())
    audit = json.loads(audit_bytes)
    manifest = json.loads(gzip.decompress((folder / 'archive-manifest.json.gz').read_bytes()))
    storage = json.loads((folder / 'storage-readback.json').read_bytes())
    assert json.loads((folder / 'native-exit.json').read_bytes())['exit_code'] == 0
    assert audit['epochs'] == 5000 and audit['parameter_count'] == 19114
    assert audit['native_float32_norms_verified'] == 5000
    assert manifest['audit_sha256'] == hashlib.sha256(audit_bytes).hexdigest()
    assert manifest['member_sha256'] == audit['sha256']
    assert manifest['native_files'] == storage['native_files_verified'] == len(audit['sha256']) == 15006
    assert storage['all_fresh_remote_members_match_native_audit']
    norm_bytes = gzip.decompress((folder / 'norms.csv.gz').read_bytes())
    assert hashlib.sha256(norm_bytes).hexdigest() == audit['norm_replay_sha256']
    archive_receipts = {Path(row['object']).name: row for row in storage['storage_objects']}
    assert len(archive_receipts) == 12
    for archive in manifest['archives']:
        receipt = archive_receipts[archive['name']]
        assert receipt['fresh_readback_exact'] and receipt['sha256'] == archive['sha256']
        assert receipt['bytes'] == archive['bytes']
    optimizer_components += audit['optimizer_components_verified']
    validation_draws += audit['validation_draws']
assert optimizer_components == 191140000 and validation_draws == 50000
baseline = json.loads((results / 'gradient-movement-replay-2026-10-18/summary.json').read_bytes())
assert baseline['seeds'] == 256 and baseline['agent_updates'] == 614400 and baseline['max_error'] == 0
perturbed = json.loads((results / 'perturbed-movement-complete-2026-10-18/combined-coverage.json').read_bytes())
assert perturbed['cases'] == 9216 and perturbed['maximum_state_error'] == 0
assert perturbed['agent_updates'] == 22118400 and perturbed['cell_updates'] == 552960000
trace = json.loads((results / 'perturbed-storage-readback-2026-10-20/audit.json').read_bytes())
assert trace['objects_verified'] == 36724 and trace['prior_replayed_cases'] == perturbed['continuation_cases'] == 9180
assert trace['all_remote_objects_match_replayed_manifest']
gradient = json.loads((results / 'gradient-ensemble-2026-10-17/audit.json').read_bytes())
assert gradient['rows'] == 115200
folder = results / 'full-predictive-comparison-2026-10-20'
summary = json.loads((folder / 'summary.json').read_bytes())
r = json.loads((folder / 'r-validation.json').read_bytes())
assert r['trajectories'] == 4000 and r['stored_states'] == 200000 and r['arithmetic_values_verified'] == 1712
storage = json.loads((folder / 'storage-readback.json').read_bytes())
assert storage['all_fresh_remote_members_match'] and storage['native_trajectories'] == 4000
truth_counts = {}
for method in ['prior', 'pathwise', 'vargrad', 'truth']:
    assert summary['distributions'][method]['draws'] == 1000
    assert summary['distributions'][method]['stored_states'] == 50000
    truth_counts[method] = sum(summary['distributions'][method]['parameters'][name]['truth_inside_pointwise_interval'] for name in ['p1', 'm_alpha', 'm_beta', 'w_alpha', 'w_beta'])
assert truth_counts['pathwise'] == 3 and truth_counts['vargrad'] == 2
visual = json.loads((folder / 'visual-review.json').read_bytes())
assert len(visual['reviewed_figures']) == 3
for name, digest in visual['reviewed_figures'].items():
    assert hashlib.sha256((folder / name).read_bytes()).hexdigest() == digest
for folder_name in ['pathwise-full-calibration-2026-10-20', 'vargrad-full-calibration-2026-10-20', 'full-predictive-comparison-2026-10-20', 'perturbed-storage-readback-2026-10-20']:
    folder = results / folder_name
    publication = json.loads((folder / 'publication.json').read_bytes())
    for name, digest in publication['files_sha256'].items():
        assert hashlib.sha256((folder / name).read_bytes()).hexdigest() == digest
for folder_name in ['native-training-qualification-2026-10-20', 'calibration-adapter-qualification-2026-10-20', 'gradient-ensemble-2026-10-17', 'gradient-movement-replay-2026-10-18', 'gradient-state-control-2026-10-18', 'perturbed-movement-complete-2026-10-18', 'perturbed-storage-readback-2026-10-20', 'pathwise-full-calibration-2026-10-20', 'vargrad-full-calibration-2026-10-20', 'full-predictive-comparison-2026-10-20']:
    for path in sorted((results / folder_name).rglob('*')):
        if path.is_file():
            pins[str(path.relative_to(results))] = hashlib.sha256(path.read_bytes()).hexdigest()
output.write_text(json.dumps({'optimizer_components': optimizer_components, 'validation_draws': validation_draws, 'gradient_baseline_seeds': 256, 'perturbed_cases': 9216, 'predictive_trajectories': 4000, 'independent_parameter_truth_interval_counts': truth_counts, 'evidence_sha256': pins, 'scope': 'Completion-review linkage audit over retained native/replay/statistical/archive evidence; not a rerun of simulations or historical numerical identity proof.'}, indent=2) + '\n')
print('Complete retained evidence links and counts verified')
