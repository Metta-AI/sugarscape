from pathlib import Path
import hashlib,json,tarfile
r=Path(__file__).resolve().parent
base=r.parent
audit_path=base/'brearcliffe-paper-table-rule-m-control-001/union-audit/audit.json'
audit=json.loads(audit_path.read_text());by_id={x['run_id']:x for x in audit['completed']};assert len(by_id)==253
extra=['released-code-pair-01-repeat-00','paper-table-pair-11-repeat-00','paper-table-pair-11-repeat-01','paper-table-pair-00-repeat-00']
with tarfile.open(r/'additional-four-inputs.tar.gz','x:gz') as tar:
    for run_id in extra:
        source=Path(by_id[run_id]['directory'])
        for p in sorted(source.rglob('*')):
            assert not p.is_symlink()
            if p.is_file():tar.add(p,arcname=run_id+'/'+str(p.relative_to(source)),recursive=False)
archives=[('local42.tar.gz',base/'brearcliffe-local42-archive-001/local42.tar.gz','97283aa4522c3d74e1cfb6ae4cbd0494cc2fe9f5e8c17f56c22890b427aaefcc'),('rule-m-recovery.tar.gz',base/'brearcliffe-rule-m-remote-recovery-001/batch-results.tar.gz','48380ec09f05a99dcff31135bcec4fd8e037b45fbc5f7d4a4adfdcf6b7276653'),('rule-m-ec.tar.gz',base/'brearcliffe-rule-m-ec-snapshot-001/pair01-49.tar.gz','8d45d7c83715aa2727ee9becb4a64e63ee22dd2e9bbdaede3c2c4e83a27506f6'),('rule-m-q.tar.gz',base/'brearcliffe-rule-m-q-snapshot-001/pair02-50.tar.gz','ef4c5fe7ac0f4489ff417feb51ac789788676da041a6296f80844d4b5c674b56'),('rule-m-sarsa.tar.gz',base/'brearcliffe-rule-m-sarsa-snapshot-001/pair03-50.tar.gz','40b9a8a59eacc87d80382f76558ea389ecd48f59617cfcde3d23a4e3294ddcc4'),('ec-rule-m.tar.gz',base/'brearcliffe-ec-rule-m-snapshot-001/pair04-50.tar.gz','53a1dd0961674d1ae95764029ba8acff1c215594e5600e4a2315ba58d0d78c19')]
archives.append(('additional-four-inputs.tar.gz',r/'additional-four-inputs.tar.gz',hashlib.sha256((r/'additional-four-inputs.tar.gz').read_bytes()).hexdigest()))
records=[];seen={}
for name,path,pin in archives:
    digest=hashlib.sha256(path.read_bytes()).hexdigest();assert digest==pin
    files={};inputs=[]
    with tarfile.open(path) as tar:
        for member in tar:
            assert member.isdir() or member.isfile()
            assert not Path(member.name).is_absolute() and '..' not in Path(member.name).parts
            if not member.isfile():continue
            body=tar.extractfile(member).read();sha=hashlib.sha256(body).hexdigest()
            assert member.name not in files
            files[member.name]={'bytes':len(body),'sha256':sha}
            if Path(member.name).name=='trajectory.csv':
                run_id=Path(member.name).parent.name
                assert run_id in by_id and run_id not in seen
                assert sha==by_id[run_id]['trajectory_sha256']
                seen[run_id]=sha;inputs.append(run_id)
    records.append({'name':name,'local_source':str(path),'bytes':path.stat().st_size,'sha256':digest,'files':files,'inputs':inputs})
assert seen.keys()==by_id.keys()
manifest={'archives':records,'inputs':253,'observations':audit['observations'],'source_audit_sha256':hashlib.sha256(audit_path.read_bytes()).hexdigest(),'scope':'Durable preservation of already audited inputs; no new simulation or coverage credit.'}
(r/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(json.dumps({'archives':len(records),'bytes':sum(x['bytes'] for x in records),'members':sum(len(x['files']) for x in records),'inputs':len(seen)}))
