from pathlib import Path
import hashlib,json,tarfile
root=Path(__file__).resolve().parent
manifest_path=root/'manifest.json'
assert hashlib.sha256(manifest_path.read_bytes()).hexdigest()=='d54bc3a3fd94cd40e914c8334f697fdf8bf2f39a8ff1b15040745c2779797c55'
manifest=json.loads(manifest_path.read_text())
reports=[];seen=set()
for entry in manifest['archives']:
    p=root/entry['name']
    assert p.stat().st_size==entry['bytes']
    assert hashlib.sha256(p.read_bytes()).hexdigest()==entry['sha256']
    files={};inputs=[]
    with tarfile.open(p) as tar:
        for member in tar:
            assert member.isdir() or member.isfile()
            assert not Path(member.name).is_absolute() and '..' not in Path(member.name).parts
            if not member.isfile():continue
            assert member.name not in files
            body=tar.extractfile(member).read()
            files[member.name]={'bytes':len(body),'sha256':hashlib.sha256(body).hexdigest()}
            if Path(member.name).name=='trajectory.csv':
                run_id=Path(member.name).parent.name
                assert run_id not in seen
                seen.add(run_id);inputs.append(run_id)
    assert files==entry['files'] and inputs==entry['inputs']
    reports.append({'archive':entry['name'],'bytes':entry['bytes'],'sha256':entry['sha256'],'members':len(files),'inputs':len(inputs)})
assert len(seen)==manifest['inputs']==50
report={'manifest_sha256':'d54bc3a3fd94cd40e914c8334f697fdf8bf2f39a8ff1b15040745c2779797c55','archives':reports,'archive_bytes':sum(x['bytes'] for x in reports),'members_verified':sum(x['members'] for x in reports),'unique_audited_inputs_preserved':len(seen),'source_audit_sha256':manifest['source_audit_sha256'],'scope':'Fresh storage download and archive-member verification. Existing trajectory audits are preserved, not rerun; no new simulation or coverage credit.'}
(root/'storage-readback.json').write_text(json.dumps(report,indent=2)+chr(10))
print(json.dumps(report))
