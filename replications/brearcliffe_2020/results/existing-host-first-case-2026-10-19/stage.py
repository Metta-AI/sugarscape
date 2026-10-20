from pathlib import Path
import csv
import hashlib
import json
import subprocess
import sys
import tarfile
root = Path(__file__).resolve().parent
archive = root / 'ensemble-input.tar.gz'
assert archive.stat().st_size == 63866
assert hashlib.sha256(archive.read_bytes()).hexdigest() == 'e425c13671f156a866eba9e034939c7072cbf8e57d16769e296bcd2d458e9af2'
with tarfile.open(archive) as tar:
    tar.extractall(root, filter='data')
payload = root / 'payload'
for name, digest in json.loads((payload / 'payload-sha256.json').read_text()).items():
    assert hashlib.sha256((payload / name).read_bytes()).hexdigest() == digest
prepared = root / 'prepared'
subprocess.run([sys.executable, str(payload / 'prepare_ensemble.py'), str(payload / 'author-model.nlogo'), str(prepared)], check=True)
manifest = prepared / 'manifest.csv'
assert hashlib.sha256(manifest.read_bytes()).hexdigest() == '3633edf2ca2ec1bd59222e15241655c38c7ec0cacffd1948294ed7c69be85c37'
with manifest.open() as file:
    expected = {row['run_id']: row for row in csv.DictReader(file)}
for row in expected.values():
    assert hashlib.sha256((prepared / row['model']).read_bytes()).hexdigest() == row['model_sha256']
assignment = payload / 'assignment.csv'
assert hashlib.sha256(assignment.read_bytes()).hexdigest() == '5f1f3154bb548d6c359931089bdf846c4ff560657b0a2ae66dcb9b0c1dfd6853'
with assignment.open() as file:
    assigned = list(csv.DictReader(file))
assert len(assigned) == 749
assert len({row['run_id'] for row in assigned}) == 749
assert all(expected[row['run_id']] == row for row in assigned)
report = {'prepared_models_verified': len(expected), 'assigned_inputs_verified': len(assigned),
          'manifest_sha256': hashlib.sha256(manifest.read_bytes()).hexdigest(),
          'assignment_sha256': hashlib.sha256(assignment.read_bytes()).hexdigest(),
          'simulation_inputs_executed': 0, 'scope': 'Staged only. Qualification and measured-budget gates still apply.'}
(root / 'staging-validation.json').write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps(report))
