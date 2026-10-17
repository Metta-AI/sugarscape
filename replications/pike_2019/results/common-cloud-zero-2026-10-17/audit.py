from pathlib import Path
import csv,hashlib,json,math,tarfile
from collections import defaultdict
root=Path(__file__).resolve().parent
archive=root/'native.tar.gz'
assert hashlib.sha256(archive.read_bytes()).hexdigest()=='774e58c19e8dcd650d2244df6b45f59468a5d3c1ad7b8619b6299ae90343c089'
with tarfile.open(archive) as t:t.extractall(root/'extracted',filter='data')
r=root/'extracted/pike-common-cloud-zero-001'
assert json.loads((r/'exit.json').read_text())['exit_code']==0
results=[]
for index,variant in enumerate(['common-one','common-multi']):
 p=r/variant;m=json.loads((p/'manifest.json').read_text())
 assert m['numpy_seed']==m['policy_random_seed']==0 and m['mesa_seed']==42
 assert m['pythonhashseed']=='0' and m['variant']==variant and m['steps']==1000
 assert m['revision']=='585e53398f4f58e89ec184c83bb20819f0e4c96a' and m['library_revision']=='99d2091721076df9fff32e8b49a0e33e98c34a6f'
 assert m['runner_sha256']==hashlib.sha256((root.parent/'pike-common-cloud-ensemble-launch-001/run.py').read_bytes()).hexdigest()
 assert json.loads((r/f'worker-{index}-exit.json').read_text())['exit_code']==0
 obs=json.loads((p/'observations.json').read_text());assert [x['step'] for x in obs]==list(range(1,1001))
 ids={x['id'] for x in json.loads((p/'initial-agents.json').read_text())};assert len(ids)==200
 health=defaultdict(set);bad=[];negative=0;count=0
 with (p/'health.csv').open() as stream:
  for row in csv.DictReader(stream):
   step,agent=int(row['Step']),int(row['Agent']);assert 1<=step<=1000 and agent not in health[step]
   health[step].add(agent);count+=1
   values=[float(row[k]) for k in ['Sugar_Level','Spice_Level']]
   if not all(math.isfinite(v) for v in values):bad.append(step)
   negative+=any(v<0 for v in values)
 for row in obs:
  current=set(row['agent_ids']);assert current<=ids and current==health[row['step']] and len(current)==len(row['agent_ids'])==row['individual_agents'];ids=current
 complete=json.loads((p/'complete.json').read_text());assert complete['steps']==1000 and complete['individual_agents']==len(ids) and complete['native_reporter']==obs[-1]['native_reporter']
 prices=json.loads((p/'prices.json').read_text());assert all(1<=int(k)<=1000 and all(math.isfinite(v) and v>0 for v in vs) for k,vs in prices.items())
 results.append({'variant':variant,'seed':0,'steps':1000,'final_individuals':len(ids),'health_records':count,'nonfinite_health_records':len(bad),'first_nonfinite_step':min(bad) if bad else None,'negative_health_records':negative,'numeric_validation':'failed' if bad else 'passed','raw_sha256':{f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in p.iterdir() if f.is_file()}})
report={'runs':results,'scope':'Source/identity/health/terminal audit of two native cloudseedzero conditions; no full-grid or paper verdict. Price values checked positive/finite; aggregate price statistics deferred to full-grid analysis.'}
(root/'audit.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
