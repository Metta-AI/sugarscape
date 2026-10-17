from pathlib import Path
import subprocess,json,os,hashlib,time
root=Path(__file__).resolve().parent
base=root.parent
runner=Path('/Users/relh/Code/workspace/sugarscape-pike/replications/pike_2019/trace_group_membership.py')
reports=[]
for policy in ['none','movement']:
 for approach in ['explicit','network']:
  target=root/(approach+'-'+policy)
  command=[str(base/'pike-runtime-001/bin/python'),str(runner),'/Users/relh/Code/workspace/sugarscape-pike-reference','/Users/relh/Code/workspace/sugarscape-pike-library-reference',approach,'10',policy,'0',str(target)]
  env=dict(os.environ,PYTHONHASHSEED='0',OPENBLAS_NUM_THREADS='1')
  started=time.time()
  result=subprocess.run(command,env=env,timeout=600)
  assert result.returncode==0
  source=base/('pike-phase2-001' if policy=='none' else 'pike-phase3-movement-001')/(approach+'-10-0'+('' if policy=='none' else '-released'))/'run'
  files=['initial-agents.json','observations.json','health.csv','prices.json','population.csv']
  hashes={name:hashlib.sha256((target/'run'/name).read_bytes()).hexdigest() for name in files}
  assert all(hashes[name]==hashlib.sha256((source/name).read_bytes()).hexdigest() for name in files)
  reports.append({'approach':approach,'policy':policy,'command':command,'elapsed_seconds':time.time()-started,'baseline':str(source),'exact_raw_sha256':hashes,'composition':json.loads((target/'composition-audit.json').read_text())})
  (root/'progress.json').write_text(json.dumps(reports,indent=2)+'\n')
(root/'complete.json').write_text(json.dumps({'validated_runs':4,'validated_steps':4000,'exact_raw_files':20,'runs':reports},indent=2)+'\n')
