"""Reconstruct the complete audited Bentham ensemble without duplicating raw inputs."""
from pathlib import Path
import gzip
import hashlib
import json
import numpy as np

root = Path(__file__).parent
coverage_path = Path('/Users/relh/Code/workspace/sugarscape-blueprints/replications/blueprints_2024/results/homogeneous-complete-2026-10-18/coverage.json')
coverage = json.loads(coverage_path.read_text())
expected = {}
for item in coverage['inputs']:
    if item['model'] != 'benthamHalfLookaheadBinary':
        continue
    audit_path = Path(item['path'])
    assert hashlib.sha256(audit_path.read_bytes()).hexdigest() == item['sha256']
    audit = json.loads(audit_path.read_text())
    for record in audit['results']:
        seed = str(record['seed'])
        if seed in expected:
            assert expected[seed] == record
        expected[seed] = record
candidates = json.loads((root / 'candidate-inputs.json').read_text())
assert set(expected) == set(candidates) and len(expected) == 500
metrics = ['population', 'agentMeanTimeToLive', 'agentStarvationDeaths', 'agentCombatDeaths', 'agentWealthTotal', 'meanAgeAtDeath', 'agentDiseaseDeaths', 'agentAgingDeaths']
values = np.zeros((500, 5001, len(metrics)))
inputs = {}
observations = 0
for index, seed in enumerate(sorted(expected, key=int)):
    record = expected[seed]
    assert candidates[seed]['record'] == record
    for candidate in candidates[seed]['candidates']:
        path = Path(candidate)
        if not path.is_file():
            continue
        raw = gzip.decompress(path.read_bytes())
        if hashlib.sha256(raw).hexdigest() == record['trajectory_sha256']:
            break
    else:
        raise AssertionError(f'No matching retained trajectory for {seed}')
    rows = json.loads(raw)
    assert [r['timestep'] for r in rows] == list(range(5001))
    assert len(rows) == record['observations'] and rows[-1]['population'] == record['final_population']
    assert all(r['seed'] == int(seed) for r in rows)
    values[index] = [[r[m] for m in metrics] for r in rows]
    observations += len(rows)
    inputs[seed] = {'record': record, 'path': str(path)}
    if index % 50 == 0:
        print(index + 1, flush=True)
assert np.isfinite(values).all() and observations == 2500500
means = values.mean(axis=0)
np.savetxt(root / 'independent-means.csv', np.column_stack([np.arange(5001),means[:,:6]]), delimiter=',', header='timestep,'+','.join(metrics[:6]), comments='')
derived = np.column_stack([(means[:,2]+means[:,3])/means[:,0],means[:,4]/means[:,0]])
np.savetxt(root / 'derived-means.csv', np.column_stack([np.arange(5001),derived]), delimiter=',', header='timestep,starvation_plus_combat_per_population,wealth_per_population', comments='')
np.savetxt(root / 'all-cause-means.csv', np.column_stack([np.arange(5001),means[:,[2,3,6,7]]]), delimiter=',', header='timestep,starvation,combat,disease,aging', comments='')
(root / 'inputs.json').write_text(json.dumps(inputs,indent=2)+'\n')
report={'model':'benthamHalfLookaheadBinary','runs':500,'observations':observations,'metrics':metrics,'coverage_sha256':hashlib.sha256(coverage_path.read_bytes()).hexdigest(),'all_native_trajectory_hashes_verified':True,'scope':'Independent complete ensemble aggregation. Released parser equivalence and published figure comparison remain unverified.'}
(root / 'audit.json').write_text(json.dumps(report,indent=2)+'\n')
(root / 'provenance.json').write_text(json.dumps({'files':{name:hashlib.sha256((root/name).read_bytes()).hexdigest() for name in ['audit.json','inputs.json','independent-means.csv','derived-means.csv','all-cause-means.csv']}},indent=2)+'\n')
print(json.dumps(report),flush=True)
