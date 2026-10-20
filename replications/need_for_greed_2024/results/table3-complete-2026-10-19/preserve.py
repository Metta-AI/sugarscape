from pathlib import Path
import hashlib
import json
import subprocess
import tarfile

root = Path(__file__).resolve().parent
name = 'five-completed.tar.gz'
source = root / name
prefix = 'relh-sugarscape-evidence-20261017/need-for-greed-utilitarian-complete-001/'
result = subprocess.run(['autor','storage','cp',str(source),prefix+name,'--json'],capture_output=True,text=True,timeout=180)
(root/'storage-upload.json').write_text(json.dumps({'exit_code':result.returncode,'stdout':result.stdout,'stderr':result.stderr},indent=2)+'\n')
assert result.returncode == 0
readback = root/'storage-readback';readback.mkdir()
result = subprocess.run(['autor','storage','cp',prefix+name,str(readback/name),'--json'],capture_output=True,text=True,timeout=180)
(root/'storage-download.json').write_text(json.dumps({'exit_code':result.returncode,'stdout':result.stdout,'stderr':result.stderr},indent=2)+'\n')
assert result.returncode == 0
raw = (readback/name).read_bytes()
assert raw == source.read_bytes()
audit = json.loads((root/'audit.json').read_bytes())
assert hashlib.sha256(raw).hexdigest() == audit['archive_sha256']
files = {}
with tarfile.open(readback/name) as archive:
    for member in archive:
        assert member.isfile() or member.isdir()
        assert not Path(member.name).is_absolute() and '..' not in Path(member.name).parts
        if not member.isfile():continue
        assert member.name not in files
        files[member.name] = hashlib.sha256(archive.extractfile(member).read()).hexdigest()
assert files == audit['member_sha256']
report = {'storage_object':prefix+name,'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest(),'members_verified':len(files),'fresh_download_exact':True,'inputs':5,'entries':[r['entry'] for r in audit['runs']],'scope':'Five completed original inputs preserved separately; future regular checkpoint overlap must be deduplicated against the current417-input inventory.'}
(root/'storage-readback.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report))
