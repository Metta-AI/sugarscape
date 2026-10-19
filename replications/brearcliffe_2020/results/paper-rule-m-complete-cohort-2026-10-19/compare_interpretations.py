"""Compare all paired native Rule M trajectories across parameter interpretations."""
from pathlib import Path
import csv
import hashlib
import json
root = Path(__file__).resolve().parent
output = root / 'paired-interpretations.json'
assert not output.exists()
audit = json.loads((root / 'union-audit/audit.json').read_text())
by_id = {r['run_id']: r for r in audit['completed']}
prepared = root.parent / 'brearcliffe-ensemble-preparation-001'
with (prepared / 'manifest.csv').open() as stream:
    manifest = {r['run_id']: r for r in csv.DictReader(stream)}
comparisons = []
for repetition in range(50):
    ids = [f'{interpretation}-pair-00-repeat-{repetition:02d}' for interpretation in ('released-code','paper-table')]
    rows = [manifest[key] for key in ids]
    assert rows[0]['seed'] == rows[1]['seed']
    assert all(r['group_A'] == r['group_B'] == 'Rule M' and r['steps'] == '20000' for r in rows)
    assert [(r['learning_rate'],r['gamma']) for r in rows] == [('0.9','0.8'),('0.8','0.9')]
    paths = [Path(by_id[key]['directory']) / 'trajectory.csv' for key in ids]
    raw = [p.read_bytes() for p in paths]
    hashes = [hashlib.sha256(value).hexdigest() for value in raw]
    comparisons.append({'repetition':repetition,'seed':int(rows[0]['seed']),'released_run':ids[0],'paper_run':ids[1],'released_sha256':hashes[0],'paper_sha256':hashes[1],'raw_bytes_equal':raw[0]==raw[1],'observations_per_trajectory':20001})
report = {'paired_runs':50,'observations_per_interpretation':1000050,'byte_exact_pairs':sum(r['raw_bytes_equal'] for r in comparisons),'comparisons':comparisons,'audit_sha256':hashlib.sha256((root/'union-audit/audit.json').read_bytes()).hexdigest(),'scope':'Paired full-trajectory equality check of non-learning Rule M control only. Does not establish equivalence for learning agents or reproduce paper results.'}
output.write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k!='comparisons'}))
