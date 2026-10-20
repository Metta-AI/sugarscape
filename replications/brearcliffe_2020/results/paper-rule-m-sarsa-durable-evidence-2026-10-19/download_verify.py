from pathlib import Path
import json
import shutil
import subprocess
import sys
root = Path(__file__).resolve().parent
manifest = json.loads((root / 'manifest.json').read_text())
assert shutil.disk_usage(root).free > sum(x['bytes'] for x in manifest['archives']) + 512 * 1024**2
assert all(x['exit_code'] == 0 for x in json.loads((root / 'upload-receipts.json').read_text()))
readback = root / 'storage-readback'
readback.mkdir()
for name in [x['name'] for x in manifest['archives']] + ['manifest.json']:
    result = subprocess.run(['autor', 'storage', 'cp', 'relh-sugarscape-evidence-20261017/' + root.name + '/' + name, str(readback / name), '--json'], capture_output=True, text=True, timeout=180)
    (root / (name + '.download.json')).write_text(json.dumps({'exit_code': result.returncode, 'stdout': result.stdout, 'stderr': result.stderr}, indent=2) + '\n')
    assert result.returncode == 0
shutil.copyfile(root / 'verify_storage.py', readback / 'verify_storage.py')
subprocess.run([sys.executable, str(readback / 'verify_storage.py')], check=True, timeout=60)
shutil.copyfile(readback / 'storage-readback.json', root / 'storage-readback.json')
