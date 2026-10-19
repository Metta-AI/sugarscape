from pathlib import Path
import hashlib
import json
import subprocess
import sys
import tarfile

root = Path(__file__).resolve().parent
archive = root / 'checkpoint-0275.tar.gz'
assert archive.stat().st_size == 8851654
assert hashlib.sha256(archive.read_bytes()).hexdigest() == 'cc09f9039d569bb6365c5b9f70f6898097361947dfe169a251b2365ce3a7b9ad'
result = root / 'verified'
result.mkdir()
members = {}
for pass_number in (1, 2):
    extracted = root / f'extracted-{pass_number}'
    extracted.mkdir()
    with tarfile.open(archive) as tar:
        for member in tar.getmembers():
            assert not Path(member.name).is_absolute() and '..' not in Path(member.name).parts
            assert member.isdir() or member.isfile()
        tar.extractall(extracted, filter='data')
    current = {str(p.relative_to(extracted)): hashlib.sha256(p.read_bytes()).hexdigest()
               for p in sorted(extracted.rglob('*')) if p.is_file()}
    if pass_number == 1:
        members = current
    else:
        assert current == members
    runs = sorted((extracted / 'runs').iterdir())
    assert len(runs) == 25
    for run in runs:
        output = result / f'audits-{pass_number}' / run.name
        subprocess.run([sys.executable, str(root / 'audit_supplement.py'), str(root.parent / 'blueprints-heterogeneous50-remote-audit-001' / 'original.zip'),
                        str(run), str(output), '--expected-runtime', 'pypy'], check=True,
                       stdout=subprocess.DEVNULL)
        assert (output / 'audit.json').read_bytes() == (extracted / 'audits' / run.name / 'audit.json').read_bytes()
        if pass_number == 2:
            assert (output / 'audit.json').read_bytes() == (result / 'audits-1' / run.name / 'audit.json').read_bytes()
    print(json.dumps({'pass': pass_number, 'inputs': len(runs), 'members': len(current)}), flush=True)
(result / 'members.json').write_text(json.dumps(members, indent=2) + '\n')
summary = {'fresh_extractions': 2, 'archive_members_verified': len(members), 'inputs_per_pass': 25,
           'producer_and_two_independent_audits_byte_identical': True,
           'archive_sha256': hashlib.sha256(archive.read_bytes()).hexdigest(),
           'auditor_sha256': hashlib.sha256((root / 'audit_supplement.py').read_bytes()).hexdigest(),
           'original_archive_sha256': hashlib.sha256((root.parent / 'blueprints-heterogeneous50-remote-audit-001' / 'original.zip').read_bytes()).hexdigest(),
           'python': sys.version, 'scope': 'Trajectory audit only; union and overlap checks remain separate.'}
(result / 'validation.json').write_text(json.dumps(summary, indent=2) + '\n')
with tarfile.open(root / 'verified.tar.gz', 'w:gz') as tar:
    tar.add(result, arcname='verified')
print(json.dumps(summary))
