"""Select the complete original 0.36 cohort from already audited sealed archives."""
from pathlib import Path
import gzip
import hashlib
import json
import tarfile

root = Path(__file__).resolve().parent
base = root.parent
inventory_path = base / 'need-for-greed-table4-prefix-004/reconciliation.json'
inventory = json.loads(inventory_path.read_bytes())
wanted = {r['entry']: r for r in inventory['runs'] if r['entry'].startswith('0.36-')}
inputs_path = base / 'need-for-greed-remaining-plan-001/prepared/inputs.json.gz'
original = json.loads(gzip.decompress(inputs_path.read_bytes()))
assert set(wanted) == {r['entry'] for r in original if r['entry'].startswith('0.36-')}
assert len(wanted) == 100
rows = []
archive_hashes = {}
sources = {}
for folder in ['need-for-greed-table4-pilots-001'] + [f'need-for-greed-table4-prefix-{i:03}' for i in range(1, 5)]:
    directory = base / folder
    audit_path = directory / ('readback.json' if 'pilots' in folder else 'audit.json')
    audit = json.loads(audit_path.read_bytes())
    sources[str(audit_path)] = hashlib.sha256(audit_path.read_bytes()).hexdigest()
    archives = list(directory.glob('*.tar.gz'))
    assert len(archives) == 1
    archive_path = archives[0]
    digest = hashlib.sha256(archive_path.read_bytes()).hexdigest()
    assert digest == audit['archive_sha256']
    archive_hashes[str(archive_path)] = digest
    audited = {r['entry']: r for r in audit['runs']}
    with tarfile.open(archive_path) as archive:
        for member in archive.getmembers():
            if not member.name.endswith('-pypy/manifest.json'):
                continue
            manifest = json.loads(archive.extractfile(member).read())
            entry = manifest['entry']
            if entry not in wanted:
                continue
            assert manifest['release'] == 'b9ca671ab7591c7b3606f2d76c33eda344d626d1'
            r = audited[entry]
            assert all(r[k] == wanted[entry][k] for k in wanted[entry])
            rows.append(dict(r, native_archive=str(archive_path), manifest_member=member.name))
assert len(rows) == len({r['entry'] for r in rows}) == 100
assert {r['entry'] for r in rows} == set(wanted)
report = dict(native_inputs=100, condition=0.36, runs=sorted(rows,key=lambda r:r['entry']), native_archive_sha256=archive_hashes, source_audits_sha256=sources, inventory_sha256=hashlib.sha256(inventory_path.read_bytes()).hexdigest(), original_inputs_sha256=hashlib.sha256(inputs_path.read_bytes()).hexdigest(), observations=sum(r['observations'] for r in rows))
(root/'cohort.json').write_text(json.dumps(report,indent=2)+'\n')
for name in ['aggregate.py','validate_numpy.py','compare.py']:
    source = (base/'need-for-greed-metrics-001'/name).read_text()
    source = source.replace('== 0.37','== 0.36').replace('0.37 * box.width','0.36 * box.width').replace('vertices[37]','vertices[36]').replace('paper_centerline_at_037','paper_centerline_at_036').replace('metrics["observations"] == 495265',f'metrics["observations"] == {report["observations"]}')
    (root/name).write_text(source)
source = (base/'need-for-greed-figure2-001/extract.py').read_text().replace('0.37','0.36').replace('records[37]','records[36]')
(root/'extract.py').write_text(source)
print(json.dumps({'inputs':100,'observations':report['observations'],'archives':len(archive_hashes)}))
