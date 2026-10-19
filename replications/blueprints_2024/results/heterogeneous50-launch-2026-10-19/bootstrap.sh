#!/bin/bash
set -eu
cd /root/sugarscape/blueprints-heterogeneous50-batch-001
ln -s /root/sugarscape/blueprints-selfishness037-batch-001/cpython cpython
ln -s /root/sugarscape/blueprints-selfishness037-batch-001/pypy pypy
ln -s /root/sugarscape/blueprints-selfishness037-batch-001/engine engine
ln -s /root/sugarscape/blueprints-heterogeneous-runtime-001/original-heterogeneous.zip blueprints-heterogeneous.zip
cpython/bin/python - <<'PYCODE'
from pathlib import Path
import hashlib,json,zipfile,shutil
p=json.loads(Path('protocol.json').read_bytes())
a=Path('blueprints-heterogeneous.zip')
assert hashlib.sha256(a.read_bytes()).hexdigest()==p['original_archive_sha256']
assert shutil.disk_usage('.').free >= 8*1024**3
Path('inputs').mkdir()
with zipfile.ZipFile(a) as z:
 for row in p['inputs']:
  raw=z.read(row['entry'])
  assert hashlib.sha256(raw).hexdigest()==row['configuration_sha256']
  Path('inputs',row['entry']).write_bytes(raw)
PYCODE
exec cpython/bin/python run_supplement_batch.py .
