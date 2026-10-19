"""Exercise archive auditing through complete real-output and corrupted-output workflows."""
from pathlib import Path
import io
import json
import subprocess
import sys
import tarfile

root = Path(__file__).resolve().parent
original = root / 'audit-prefix-001.tar.gz'
modified = root / 'deliberately-corrupted.tar.gz'
changed = []
with tarfile.open(original) as source, tarfile.open(modified, 'x:gz') as target:
    for member in source.getmembers():
        if member.isfile():
            raw = source.extractfile(member).read()
            if not changed and member.name.endswith('/trajectory.json'):
                records = json.loads(raw)
                records[-1]['population'] += 1
                raw = json.dumps(records).encode()
                member.size = len(raw)
                changed.append(member.name)
            target.addfile(member, io.BytesIO(raw))
        else:
            target.addfile(member)
assert len(changed) == 1
output = root / 'corrupted-audit.json'
command = [sys.executable, str(root / 'audit.py'), str(root.parent), str(modified), str(output)]
process = subprocess.run(command, capture_output=True, text=True)
report = {'command': command, 'changed_member': changed[0], 'exit_code': process.returncode, 'stdout': process.stdout, 'stderr': process.stderr, 'output_written': output.exists()}
(root / 'qualification.json').write_text(json.dumps(report, indent=2) + '\n')
assert process.returncode != 0 and not output.exists()
assert 'digest == frozen' in process.stderr
assert (root / 'audit.json').read_bytes() == (root / 'audit-repeat.json').read_bytes()
print('Original complete archive passes twice; altered trajectory rejected without result credit.')
