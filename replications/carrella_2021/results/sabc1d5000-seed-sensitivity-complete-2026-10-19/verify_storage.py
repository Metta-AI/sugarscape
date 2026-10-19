from pathlib import Path
import hashlib
import json
import tarfile

root = Path(__file__).resolve().parent
manifest_path = root / 'archive-validation.json'
assert hashlib.sha256(manifest_path.read_bytes()).hexdigest() == '2623f0a653f2bd54c3a81ee8ec039db41390b6ca9d72cd302a3addc52855ea76'
report = json.loads(manifest_path.read_text())
archive = root / 'native-evidence.tar.gz'
assert archive.stat().st_size == report['archive_bytes'] == 174476952
assert hashlib.sha256(archive.read_bytes()).hexdigest() == report['archive_sha256'] == '4227a260533e1e33ed398210fd4733c898c8bfbdfe6f06d1d9abb58145cb080e'
seen = set()
with tarfile.open(archive, 'r|gz') as bundle:
    for member in bundle:
        assert member.isfile() and member.name not in seen
        data = bundle.extractfile(member).read()
        pin = report['source_hashes'][member.name]
        assert len(data) == pin['bytes'] and hashlib.sha256(data).hexdigest() == pin['sha256']
        seen.add(member.name)
assert seen == report['source_hashes'].keys() and len(seen) == 157
result = {'archive_bytes': archive.stat().st_size, 'archive_sha256': report['archive_sha256'], 'archive_members_verified': len(seen), 'manifest_sha256': '2623f0a653f2bd54c3a81ee8ec039db41390b6ca9d72cd302a3addc52855ea76', 'scope': 'Fresh object-storage import independently verifies archive and every member byte hash; numerical audits remain separately recorded.'}
(root / 'storage-readback-validation.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(result))
