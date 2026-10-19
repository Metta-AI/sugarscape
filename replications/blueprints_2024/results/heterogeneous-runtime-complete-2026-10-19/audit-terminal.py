from pathlib import Path
import hashlib,json,subprocess,tarfile,shutil
repo=Path('/Users/relh/Code/workspace/sugarscape-blueprints')
root=repo.parent/'sugarscape-replication-evidence/blueprints-heterogeneous-runtime-001'
receipts=root.parent/'storage-handoff-20261017-001/blueprints-heterogeneous-runtime-001'
base=repo/'replications/blueprints_2024'
out=base/'results/heterogeneous-runtime-complete-2026-10-19'
name='terminal-evidence.tar.gz'
intent=json.loads((receipts/(name+'.intent.json')).read_bytes());status=json.loads((receipts/(name+'.status.json')).read_bytes());terminal=json.loads((receipts/'terminal.json').read_bytes())
assert status['status']=='complete' and terminal['exit_code']==0
archive=root/name
assert not archive.exists()
subprocess.run(['autor','storage','cp','relh-sugarscape-evidence-20261017/'+intent['destination'],str(archive)],check=True)
assert archive.stat().st_size==status['bytes_transferred']==intent['receipt']['bytes']
assert hashlib.sha256(archive.read_bytes()).hexdigest()==intent['receipt']['sha256']
extracted=root/'downloaded-terminal';extracted.mkdir();hashes={}
with tarfile.open(archive) as tar:
 for m in tar:
  assert m.isfile() and not Path(m.name).is_absolute() and '..' not in Path(m.name).parts
  raw=tar.extractfile(m).read();p=extracted/m.name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(raw);hashes[m.name]=hashlib.sha256(raw).hexdigest()
assert (extracted/'protocol.json').read_bytes()==(root/'protocol.json').read_bytes()
plan=json.loads((extracted/'protocol.json').read_bytes());producer=json.loads((extracted/'summary.json').read_bytes())
for f,h in plan['frozen_files'].items():assert hashlib.sha256((extracted/f).read_bytes()).hexdigest()==h
assert len(producer['records'])==6 and producer['all_runs_audited']
assert all(r['exit_code']==r['audit_exit_code']==0 for r in producer['records'])
out.mkdir();python=str(repo.parent/'sugarscape-replications/.venv/bin/python');original=root.parent/'papers/blueprints-heterogeneous.zip'
prior=json.loads((base/'results/selfishness037-terminal-prefix-2026-10-19/inventory/inventory.json').read_bytes())
prior_rows={r['entry']:r for r in prior['excluded_controls'] if r['experiment']=='heterogeneous'}
observations=0;comparisons=[]
for row in plan['inputs']:
 pair=[];audits=[]
 for runtime in ['cpython','pypy']:
  run=row['entry'].removesuffix('.config')+'-'+runtime
  command=[python,str(base/'audit_supplement.py'),str(original),str(extracted/'runs'/run),str(out/'audits'/run),'--expected-runtime',runtime]
  subprocess.run(command,cwd=repo,check=True,stdout=(root/(run+'-audit.log')).open('w'))
  local=json.loads((out/'audits'/run/'audit.json').read_bytes());remote=json.loads((extracted/'audits'/run/'audit.json').read_bytes());assert local==remote
  audits.append(local['validated']);observations+=local['validated']['observations'];pair.append((extracted/'runs'/run/'trajectory.json').read_bytes())
 assert pair[0]==pair[1]
 assert audits[0]==audits[1]
 comparisons.append({'entry':row['entry'],'byte_identical':True,'trajectory_sha256':hashlib.sha256(pair[0]).hexdigest(),'matches_prior_control':hashlib.sha256(pair[0]).hexdigest()==prior_rows[row['entry']]['trajectory_sha256'],'observations_per_runtime':audits[0]['observations'],'final_timestep':audits[0]['final_timestep'],'final_population':audits[0]['final_population']})
summary={'validated_runs':6,'validated_pairs':3,'observations':observations,'comparisons':comparisons,'all_producer_local_audits_exact':True,'archive_members_verified':len(hashes),'unique_coverage_added':0,'scope':'Pinned CPython/PyPy fidelity for three full original heterogeneous controls; not all configurations, independent-engine correctness, isolated throughput or paper completion.'}
(out/'summary.json').write_text(json.dumps(summary,indent=2)+'\n');(out/'member-sha256.json').write_text(json.dumps(hashes,indent=2)+'\n')
for f in ['protocol.json','summary.json','versions.json']:shutil.copyfile(extracted/f,out/('producer-'+f))
for suffix in ['intent','status','submission']:shutil.copyfile(receipts/(name+'.'+suffix+'.json'),out/('export-'+suffix+'.json'))
shutil.copyfile(receipts/'terminal.json',out/'terminal.json');shutil.copyfile(archive,out/name)
print(json.dumps(summary,indent=2))
