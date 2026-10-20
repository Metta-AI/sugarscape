from pathlib import Path
import hashlib
import json
import subprocess
import tarfile

root = Path(__file__).resolve().parent
base = root.parent
expected = json.loads((root / 'export.json').read_text())
archive = root / 'delta.tar.gz'
assert hashlib.sha256(archive.read_bytes()).hexdigest() == expected['sha256']
assert archive.stat().st_size == expected['bytes']
download = root / 'delta'
download.mkdir()
with tarfile.open(archive) as bundle:
    bundle.extractall(download, filter='data')
python = base.parent / 'sugarscape-replications/.venv/bin/python'
script = base.parent / 'sugarscape-pike/replications/pike_2019/reconcile_segments.py'
original = base / 'pike-phase1-001'
local = base / 'pike-segment-phase1-003'
prior = base / 'pike-cloud-checkpoint-001/download/phase1-195-300'
recorded = expected['recorded_root']
command = [str(python), str(script), '1', str(root / 'reconciliation'), '--require-complete',
           '--segment', str(original), '0', str(original),
           '--segment', str(local), '194', str(local),
           '--segment', str(prior), '195', recorded,
           '--segment', str(download), '241', recorded]
(root / 'command.json').write_text(json.dumps(command, indent=2) + '\n')
with (root / 'audit.log').open('w') as log:
    subprocess.run(command, stdout=log, stderr=subprocess.STDOUT, check=True)
report = json.loads((root / 'reconciliation/reconciliation.json').read_text())
assert report['complete_grid'] and report['validated_runs'] == 300
assert not report['missing_ordinals'] and report['price_step_records'] == 300000
summary = {'archive_sha256': expected['sha256'], 'new_cloud_conditions': 59,
           'phase': 1, 'validated_runs': 300, 'required_runs': 300,
           'health_records': report['health_records'], 'price_step_records': report['price_step_records'],
           'complete_grid': True,
           'scope': 'Full frozen phase-one grid passes fresh native raw-output audits and disjoint reconciliation. No whole-paper completion or aggregate paper verdict.'}
(root / 'validation.json').write_text(json.dumps(summary, indent=2) + '\n')
print(json.dumps(summary))
