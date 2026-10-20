from pathlib import Path
import json,hashlib,subprocess,os,time
root=Path(__file__).parent
base=root.parent
repo=Path('/Users/relh/Code/workspace/sugarscape-oremland/replications/oremland_2014')
python='/Users/relh/Code/workspace/sugarscape-replications/.venv/bin/python'
experiment=base/'oremland-rankings-headless-002'
pid=json.loads((experiment/'execution/manifest.json').read_text())['launcher_pid']
protocol=json.loads((experiment/'protocol.json').read_text())
names=list(dict.fromkeys(j['model'] for j in protocol['jobs']))
hashes={name:hashlib.sha256((repo/name).read_bytes()).hexdigest() for name in ['audit_ranking_model.py','analyze_ranking_model.py']}
(root/'process.json').write_text(json.dumps({'pid':os.getpid(),'producer_pid':pid,'models':names,'source_sha256':hashes,'wait_seconds':4000},indent=2)+'\n')
deadline=time.monotonic()+4000
with (root/'run.log').open('x') as log,(root/'progress.jsonl').open('x') as progress:
 for name in names:
  exits=[experiment/'execution'/f'{name}-shard-{i}.exit.json' for i in range(4)]
  while not all(p.exists() for p in exits) and time.monotonic()<deadline:
   os.kill(pid,0);time.sleep(5)
  assert all(p.exists() for p in exits)
  for filename,digest in hashes.items():assert hashlib.sha256((repo/filename).read_bytes()).hexdigest()==digest
  audit=base/'oremland-headless-audits-001'/name
  analysis=base/'oremland-headless-analysis-001'/name
  subprocess.run([python,str(repo/'audit_ranking_model.py'),str(experiment),name,str(audit)],stdout=log,stderr=subprocess.STDOUT,check=True,timeout=600)
  subprocess.run([python,str(repo/'analyze_ranking_model.py'),str(base/'oremland-convergence-002'),str(audit),str(analysis)],stdout=log,stderr=subprocess.STDOUT,check=True,timeout=300)
  compared=0
  for shard in range(4):
   filename=f'{name}-shard-{shard}.results.jsonl'
   with (base/'oremland-rankings-001/execution'/filename).open() as old,(experiment/'execution'/filename).open() as new:
    for a,b in zip(old,new):
     before=json.loads(a);after=json.loads(b)
     before.pop('elapsed_seconds');after.pop('elapsed_seconds');assert before==after
     compared+=1
  record={'model':name,'complete_native_runs':json.loads((audit/'audit.json').read_text())['complete_native_runs'],'exact_retained_prefix_results':compared}
  progress.write(json.dumps(record)+'\n');progress.flush()
(root/'exit.json').write_text(json.dumps({'exit_code':0,'models_processed':len(names)},indent=2)+'\n')
