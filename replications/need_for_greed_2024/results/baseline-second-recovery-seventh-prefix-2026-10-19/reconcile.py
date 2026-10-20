"""Reconcile unique original inputs and report the incomplete Table IV bin."""
from pathlib import Path
from collections import Counter
import gzip
import hashlib
import json

root = Path(__file__).resolve().parent
base = root.parent
previous_path = base / 'need-for-greed-table4-prefix-006/reconciliation.json'
previous = json.loads(previous_path.read_bytes())
new = json.loads((root / 'audit.json').read_bytes())
new_runs = new['runs']
assert len(new_runs) == len({r['entry'] for r in new_runs}) == 25
assert {r['entry'] for r in previous['runs']}.isdisjoint(r['entry'] for r in new_runs)
keys = ('entry', 'observations', 'trajectory_sha256', 'final_population')
runs = previous['runs'] + [{key: row[key] for key in keys} for row in new_runs]
assert len(runs) == len({r['entry'] for r in runs}) == 537
inputs = json.loads(gzip.decompress((base / 'need-for-greed-remaining-plan-001/prepared/inputs.json.gz').read_bytes()))
lookup = {r['entry']: r for r in inputs}
assert len(lookup) == 10500 and {r['entry'] for r in runs} <= lookup.keys()
counts = Counter(lookup[r['entry']]['kind'] for r in runs)
assert counts == {'baseline':282,'sweep':255}
table_runs = [r for r in runs if r['entry'][0].isdigit() and 0.36 <= float(r['entry'].split('-')[0]) <= 0.40]
assert len(table_runs) == 252
outcomes = Counter('extinct' if r['final_population']==0 else 'worse' if r['final_population']<=250 else 'better' for r in table_runs)
levels = Counter(r['entry'].split('-')[0] for r in table_runs)
result = {'audited_inputs':len(runs),'audited_observations':sum(r['observations'] for r in runs),'new_inputs':25,'new_observations':sum(r['observations'] for r in new_runs),'partition_counts':{k:{'audited':counts[k],'remaining':sum(r['kind']==k for r in inputs)-counts[k]} for k in ('baseline','sweep')},'runs':runs,'overlap':[],'source_sha256':{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in (previous_path,root/'audit.json')},'table4_partial':{'audited_inputs':252,'required_inputs':500,'counts_by_level':dict(levels),'outcomes':dict(outcomes),'exactly_initial_population':sum(r['final_population']==250 for r in table_runs)},'scope':'Original inputs counted once, excluding previously credited pilots and checkpoints. Partial bin is ordered by execution, not a representative sample. No full-table comparison or completed-paper credit.'}
(root/'reconciliation.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k not in ('runs','source_sha256')}))
