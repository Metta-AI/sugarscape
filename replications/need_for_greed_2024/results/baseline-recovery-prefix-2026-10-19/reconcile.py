"""Add independently audited recovered inputs to the existing unique-input inventory."""
from pathlib import Path
import gzip
import hashlib
import json
import sys

base, output = map(Path, sys.argv[1:])
assert not output.exists()
old_path = base / 'need-for-greed-endpoint-recovery-001/reconciliation.json'
new_path = base / 'need-for-greed-baseline-audit-001/audit.json'
old = json.loads(old_path.read_bytes())
new = json.loads(new_path.read_bytes())
inputs_path = base / 'need-for-greed-remaining-plan-001/prepared/inputs.json.gz'
inputs = json.loads(gzip.decompress(inputs_path.read_bytes()))
assert len(inputs) == len({r['entry'] for r in inputs}) == 10500
assert len(old['runs']) == old['audited_inputs'] == 170
assert len(new['runs']) == new['inputs'] == 22
runs = old['runs'] + new['runs']
assert len({r['entry'] for r in runs}) == len(runs)
names = {r['entry'] for r in runs}
assert names <= {r['entry'] for r in inputs}
counts = {kind: sum(r['kind'] == kind and r['entry'] in names for r in inputs) for kind in ('baseline', 'sweep')}
assert counts == {'baseline': 89, 'sweep': 103}
result = {'audited_inputs': len(runs), 'audited_observations': sum(r['observations'] for r in runs), 'new_inputs': new['inputs'], 'new_observations': new['observations'], 'partition_counts': {kind: {'audited': counts[kind], 'remaining': sum(r['kind'] == kind for r in inputs) - counts[kind]} for kind in counts}, 'overlap': [], 'runs': runs, 'source_sha256': {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in (old_path, new_path, inputs_path)}, 'scope': '22 recovered baselines reconciled by unique original entry. Later checkpoints must deduplicate these entries. Table IV pilots remain outside coverage. No completed-paper credit.'}
output.write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps({k: v for k,v in result.items() if k not in ('runs', 'source_sha256')}))
