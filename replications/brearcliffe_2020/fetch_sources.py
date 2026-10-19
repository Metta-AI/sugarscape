"""Recover the pinned author release and manuscript without changing their contents or notices."""

import argparse
import hashlib
import json
from pathlib import Path
import urllib.request
import zipfile

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('new_output', type=Path)
args = parser.parse_args()
audit = json.loads(Path(__file__).with_name('source-audit.json').read_text())
args.new_output.mkdir()
receipts = {}
for name, source in [('release-download', 'archive'), ('paper.pdf', 'author_manuscript')]:
    url = audit['sources'][source]
    request = urllib.request.Request(url, headers={'User-Agent': 'Sugarscape-replication-source-recovery/1.0'})
    with urllib.request.urlopen(request, timeout=60) as response:
        content = response.read(8 * 1024**2 + 1)
        receipt = {'requested_url': url, 'resolved_url': response.url,
                   'status': response.status, 'bytes': len(content),
                   'sha256': hashlib.sha256(content).hexdigest()}
    (args.new_output / name).write_bytes(content)
    receipts[name] = receipt
    (args.new_output / 'download-receipts.json').write_text(json.dumps(receipts, indent=2) + '\n')
    assert len(content) <= 8 * 1024**2
    assert receipt['bytes'] == audit['files'][name]['bytes']
    assert receipt['sha256'] == audit['files'][name]['sha256']
expected = {name.removeprefix('release/'): pin for name, pin in audit['files'].items()
            if name.startswith('release/')}
with zipfile.ZipFile(args.new_output / 'release-download') as archive:
    assert sorted(archive.namelist()) == sorted(expected)
    for name, pin in expected.items():
        content = archive.read(name)
        assert len(content) == pin['bytes']
        assert hashlib.sha256(content).hexdigest() == pin['sha256']
        destination = args.new_output / 'release' / name
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(content)
report = {'downloaded_artifacts': 2, 'verified_release_files': len(expected),
          'source_audit_sha256': hashlib.sha256(Path(__file__).with_name('source-audit.json').read_bytes()).hexdigest(),
          'release_files': expected, 'scope': 'Pinned author bytes recovered, including unmodified license and citation. No simulation or replication verdict.'}
(args.new_output / 'validation.json').write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps({'downloaded_artifacts': 2, 'verified_release_files': len(expected)}))
