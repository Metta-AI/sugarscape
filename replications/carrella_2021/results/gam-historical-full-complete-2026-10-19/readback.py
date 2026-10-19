from pathlib import Path
import hashlib
import json
import os
import subprocess
import sys
import tarfile
import time

base = Path(__file__).resolve().parent.parent
collector = base / 'storage-handoff-20261017-001/carrella-gam-historical-full-001'
root = base / 'carrella-gam-historical-full-readback-001'
root.mkdir()
deadline = time.monotonic() + 180
while not (collector / 'terminal.json').exists():
    assert time.monotonic() < deadline, 'Export observation expired; inspect original collector without restarting producer'
    time.sleep(10)
terminal = json.loads((collector / 'terminal.json').read_text())
assert terminal['exit_code'] == 0 and terminal['state'] == 'exited'
receipt = json.loads((collector / 'results.tar.gz.intent.json').read_text())['receipt']
status = json.loads((collector / 'results.tar.gz.status.json').read_text())
assert status['status'] == 'complete' and status['bytes_transferred'] == receipt['bytes']
assert receipt['bytes'] == 4581658 and receipt['sha256'] == '672400a2a9123f594637b2dce298590b54321a95093686bb1154c2f44dca46a0'
archive = root / 'results.tar.gz'
command = ['autor', 'storage', 'cp', 'relh-sugarscape-evidence-20261017/carrella-gam-historical-full-001/results.tar.gz', str(archive), '--json']
x = subprocess.run(command, capture_output=True, text=True, timeout=120)
(root / 'download.json').write_text(json.dumps({'command': command, 'exit_code': x.returncode, 'stdout': x.stdout, 'stderr': x.stderr}, indent=2) + '\n')
assert x.returncode == 0
assert archive.stat().st_size == receipt['bytes'] and hashlib.sha256(archive.read_bytes()).hexdigest() == receipt['sha256']
native = root / 'native'
native.mkdir()
with tarfile.open(archive) as bundle:
    members = {}
    for member in bundle:
        assert member.isfile() or member.isdir()
        assert not Path(member.name).is_absolute() and '..' not in Path(member.name).parts
        if member.isfile():
            body = bundle.extractfile(member).read()
            assert member.name not in members
            members[member.name] = {'bytes': len(body), 'sha256': hashlib.sha256(body).hexdigest()}
    bundle.extractall(native, filter='data')
assert {str(p.relative_to(native)): {'bytes': p.stat().st_size, 'sha256': hashlib.sha256(p.read_bytes()).hexdigest()} for p in native.rglob('*') if p.is_file()} == members
assert json.loads((native / 'terminal.json').read_text())['exit_code'] == 0
preparation = json.loads((base / 'carrella-gam-historical-full-preparation-001/protocol.json').read_text())
for name, entry in preparation['files'].items():
    assert members[name] == {'bytes': entry['bytes'], 'sha256': entry['sha256']}
assert 'R version 4.0.5' in (native / 'runtime.txt').read_text()
repo = Path('/Users/relh/Code/workspace/sugarscape-carrella/replications/carrella_2021')
command = ['/opt/homebrew/bin/Rscript', '--vanilla', str(repo / 'audit_replayed_gam.R'), str(native / 'inputs'), str(native / 'run'), str(repo / 'published_table8.json'), str(root / 'audit')]
x = subprocess.run(command, env=dict(os.environ, R_LIBS_USER='/Users/relh/Code/workspace/sugarscape-replication-tools/R-library'), capture_output=True, text=True, timeout=60)
(root / 'audit-command.json').write_text(json.dumps({'command': command, 'exit_code': x.returncode, 'stdout': x.stdout, 'stderr': x.stderr}, indent=2) + '\n')
assert x.returncode == 0
(root / 'archive-readback.json').write_text(json.dumps({'receipt': receipt, 'terminal': terminal, 'members': members, 'frozen_payload_members_exact': len(preparation['files']), 'scope': 'Fresh completed historical archive download, exact frozen input/source verification and full saved-fold arithmetic audit. Not proof of the author historical environment.'}, indent=2) + '\n')
print('Historical full replay archive and five-fold audit complete', flush=True)
