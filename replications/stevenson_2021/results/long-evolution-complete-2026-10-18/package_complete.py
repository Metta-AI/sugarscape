from pathlib import Path
import json,subprocess,time,os,hashlib,tarfile,shutil
base=Path('/Users/relh/Code/workspace');ev=base/'sugarscape-replication-evidence';root=ev/'stevenson-long-evolution-001';study=base/'sugarscape-stevenson/replications/stevenson_2021';analysis=ev/'stevenson-long-evolution-analysis-001';compare=ev/'stevenson-table1-comparison-001'
source=study/'compare_table1.py';digest=hashlib.sha256(source.read_bytes()).hexdigest();start=time.monotonic()
while not (root/'analysis-exit.json').exists():
 if not (root/'complete.json').exists(): os.kill(38271,0)
 assert time.monotonic()-start<1000
 time.sleep(10)
assert json.loads((root/'analysis-exit.json').read_text())['exit_code']==0
assert hashlib.sha256(source.read_bytes()).hexdigest()==digest
cmd=[str(base/'sugarscape-replications/.venv/bin/python'),str(source),str(ev/'papers/stevenson-2021-source-v2/ssc2021xNojpg.tex'),str(analysis),str(compare)]
result=subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
(root/'table1-comparison.log').write_text(result.stdout)
(root/'table1-comparison-exit.json').write_text(json.dumps({'command':cmd,'exit_code':result.returncode})+'\n')
assert result.returncode==0
out=study/'results/long-evolution-complete-2026-10-18';out.mkdir()
shutil.copytree(analysis,out/'analysis');shutil.copytree(compare,out/'table1')
for name in ['protocol.json','manifest.json','qualification.json','complete.json','completed.jsonl','analysis-exit.json','table1-comparison-exit.json','package_complete.py']:
 shutil.copy2(root/name,out/name)
for name in ['analyze_long_evolution.py','compare_table1.py']:shutil.copy2(study/name,out/name)
manifest=json.loads((root/'manifest.json').read_text());paths=set(manifest['sha256'])|{'manifest.json','qualification.json','completed.jsonl','complete.json'}
records=[json.loads(s) for s in (root/'completed.jsonl').read_text().splitlines()];assert len(records)==200
for r in records:
 for name,d in r['sha256'].items():
  p=f"runs/{r['scenario']}-{r['seed']}/{name}";paths.add(p);assert hashlib.sha256((root/p).read_bytes()).hexdigest()==d
hashes={}
with tarfile.open(out/'native.tar.gz','w:gz') as tar:
 for name in sorted(paths):
  hashes[name]=hashlib.sha256((root/name).read_bytes()).hexdigest();tar.add(root/name,arcname=name)
with tarfile.open(out/'native.tar.gz') as tar:
 assert set(tar.getnames())==set(hashes)
 for m in tar:assert hashlib.sha256(tar.extractfile(m).read()).hexdigest()==hashes[m.name]
(out/'archive-audit.json').write_text(json.dumps({'sha256':hashlib.sha256((out/'native.tar.gz').read_bytes()).hexdigest(),'member_sha256':hashes,'native_runs':200},indent=2)+'\n')
(root/'packaging-exit.json').write_text(json.dumps({'exit_code':0,'output':str(out)})+'\n')
print('Complete evidence packaged',out)
