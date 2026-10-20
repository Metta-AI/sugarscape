from pathlib import Path
import hashlib
import json
import subprocess
import sys

root = Path(__file__).resolve().parent
original = root.parent / 'brearcliffe-existing-host-ensemble-001'
prepare = original / 'payload/prepare_ensemble.py'
assert hashlib.sha256(prepare.read_bytes()).hexdigest() == 'bbdeb37c7300e4ca7e409cf13b752009d50aa2f08e8f5086197a496f3fef8e37'
assert hashlib.sha256((root / 'author-model.nlogo').read_bytes()).hexdigest() == 'fff5aa29aed92ee4ae04978b643e46d8316e26ca08771adb00c73ee5f2f9b28a'
subprocess.run([sys.executable, str(prepare), str(root / 'author-model.nlogo'), str(root / 'prepared')], check=True)
actual = {str(p.relative_to(root / 'prepared')): hashlib.sha256(p.read_bytes()).hexdigest()
          for p in (root / 'prepared').rglob('*') if p.is_file()}
assert len(actual) == 1602
assert all(hashlib.sha256((original / 'prepared' / name).read_bytes()).hexdigest() == digest
           for name, digest in actual.items())
report = {'regenerated_files': len(actual), 'all_files_equal_to_live_frozen_preparation': True,
          'manifest_sha256': actual['manifest.csv'], 'prepare_script_sha256': 'bbdeb37c7300e4ca7e409cf13b752009d50aa2f08e8f5086197a496f3fef8e37',
          'scope': 'Newly downloaded original model regenerates the complete pinned ensemble without simulation.'}
(root / 'preparation-validation.json').write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps(report))
