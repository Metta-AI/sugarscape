from pathlib import Path
import collections
import hashlib
import json
import sys
import zipfile

workspace, evidence, inventory_path = map(Path, sys.argv[1:])
report = json.loads(inventory_path.read_text())
blueprints = workspace / 'sugarscape-blueprints/replications/blueprints_2024'
coverage_path = blueprints / 'results/homogeneous-complete-2026-10-18/coverage.json'
assert hashlib.sha256(coverage_path.read_bytes()).hexdigest() == report['coverage_sha256']
coverage = json.loads(coverage_path.read_text())
pin = json.loads((blueprints / 'source-sha256.json').read_text())
assert pin['release'] == 'b9ca671ab7591c7b3606f2d76c33eda344d626d1'
assert report['source_sha256'] == pin['source_sha256']
results = {}
for entry in coverage['inputs']:
    path = Path(entry['path'])
    assert hashlib.sha256(path.read_bytes()).hexdigest() == entry['sha256']
    audit = json.loads(path.read_text())
    assert audit['model'] == entry['model'] and audit['source_sha256'] == pin['source_sha256']
    for row in audit['results']:
        key = (audit['model'], row['seed'])
        result = {k: row[k] for k in ['seed', 'final_population', 'trajectory_sha256', 'observations']}
        if key in results:
            assert results[key] == result
        else:
            results[key] = result
assert len(results) == report['unique_existing_baseline_runs'] == 2000
assert len(coverage['inputs']) == report['audit_reports_verified'] == 378
paper = evidence / 'papers/need-for-greed.zip'
baseline = blueprints / 'results/archive-audit-2026-10-15/blueprints-homogeneous.zip'
assert hashlib.sha256(paper.read_bytes()).hexdigest() == 'e41c89ed31811b2d100c0a54f9c0110f0572a980b599e2417b2653b934fbe440'
assert hashlib.sha256(baseline.read_bytes()).hexdigest() == coverage['archive_sha256']
with zipfile.ZipFile(paper) as source, zipfile.ZipFile(baseline) as reference:
    shared = {name for name in set(source.namelist()) & set(reference.namelist()) if name.endswith('.config')}
    assert shared == {row['entry'] for row in report['runs']}
    for row in report['runs']:
        raw = source.read(row['entry'])
        assert raw == reference.read(row['entry'])
        assert hashlib.sha256(raw).hexdigest() == row['config_sha256']
        config = json.loads(raw)
        key = (row['model'], row['seed'])
        assert key == (config['agentDecisionModels'][0], config['seed'])
        assert results[key] == row['result']
        audit = Path(row['audit_path'])
        assert hashlib.sha256(audit.read_bytes()).hexdigest() == row['audit_sha256']
assert len(report['runs']) == report['candidate_shared_runs'] == 400
assert sum(row['result']['observations'] for row in report['runs']) == report['candidate_observations']
assert dict(collections.Counter(row['model'] for row in report['runs'])) == report['model_counts']
print('Verified 400 candidate shared inputs and 378 retained audit hashes; fresh raw-data reuse remains unverified.')
