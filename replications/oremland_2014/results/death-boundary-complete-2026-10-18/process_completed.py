from pathlib import Path
import json,subprocess,time,os,tarfile,hashlib,shutil,csv
base=Path('/Users/relh/Code/workspace');ev=base/'sugarscape-replication-evidence';root=ev/'oremland-negative-death-002';study=base/'sugarscape-oremland/replications/oremland_2014';py=base/'sugarscape-replications/.venv/bin/python'
started=time.monotonic()
while not (root/'execution/exit.json').exists():
    os.kill(31994,0)
    assert time.monotonic()-started<600
    time.sleep(5)
terminal=json.loads((root/'execution/exit.json').read_text());assert len(terminal['jobs'])==12
assert all(j['exit_code']==j['decompress_exit_code']==0 for j in terminal['jobs'])
audits=ev/'oremland-negative-death-audits-001';analysis=ev/'oremland-negative-death-analysis-001'
subprocess.run([str(py),str(study/'audit_ranking_model.py'),str(root),'40-independent-comparison',str(audits/'40-independent-comparison'),'--seed-design','independent','--death-boundary','negative'],check=True)
subprocess.run([str(py),str(study/'analyze_ranking_model.py'),str(audits/'50-independent-reference'),str(audits/'40-independent-comparison'),str(analysis/'40-independent-comparison'),'--reference-kind','independent'],check=True)
subprocess.run([str(py),str(study/'compare_death_boundaries.py'),str(ev/'oremland-independent-streams-001'),str(root),str(ev/'oremland-independent-audits-001'),str(audits),str(analysis/'paired')],check=True)
out=study/'results/death-boundary-complete-2026-10-18';out.mkdir()
for name in ['protocol.json','policies.json','reduction-protocol.json','prepare_death_boundary.py']:
    shutil.copy2(root/name,out/name)
for name in ['compare_death_boundaries.py','audit_ranking_model.py','analyze_ranking_model.py']:
    shutil.copy2(study/name,out/name)
shutil.copytree(audits,out/'audits');shutil.copytree(analysis,out/'analysis')
archive=out/'native.tar.gz';hashes={}
with tarfile.open(archive,'w:gz') as tar:
    for dirname in ['40-independent-comparison','50-independent-comparison','50-independent-reference','execution']:
        for p in sorted((root/dirname).rglob('*')):
            if p.is_file():
                name=str(p.relative_to(root));hashes[name]=hashlib.sha256(p.read_bytes()).hexdigest();tar.add(p,arcname=name)
with tarfile.open(archive) as tar:
    assert set(tar.getnames())==set(hashes)
    for m in tar:
        assert hashlib.sha256(tar.extractfile(m).read()).hexdigest()==hashes[m.name]
(out/'archive-audit.json').write_text(json.dumps({'archive_sha256':hashlib.sha256(archive.read_bytes()).hexdigest(),'member_sha256':hashes,'complete_native_runs':37600},indent=2)+'\n')
rows=[]
for model in ['50-independent-comparison','40-independent-comparison']:
    with (analysis/model/'rankings.csv').open() as f:
        rows.extend(x for x in csv.DictReader(f) if x['runtime_fraction']=='1' and x['scope']=='pooled' and x['ties']=='average' and x['weighting']=='linear' and x['metric']=='deaths')
print(json.dumps(rows))
print((analysis/'paired/paired-comparison.csv').read_text())
(root/'processing-exit.json').write_text(json.dumps({'exit_code':0,'native_runs':37600,'output':str(out)})+'\n')
