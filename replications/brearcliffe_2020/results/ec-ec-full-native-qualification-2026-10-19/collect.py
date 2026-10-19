from pathlib import Path
import subprocess,json,time,hashlib,csv,math
r=Path(__file__).resolve().parent; node='relh-sugarscape-runtime-memory-cpu8-20261018-v1'; deadline=time.monotonic()+720
while True:
 p=subprocess.run(['autor','api','get',f'/nodes/{node}/commands/cmd-kt7im','--json'],capture_output=True,text=True); assert p.returncode==0; d=json.loads(p.stdout); (r/'command-status.json').write_text(json.dumps(d,indent=2)+'\n')
 if d['status']=='exited':
  assert d['exit_code']==0; break
 assert d['status']=='running' and time.monotonic()<deadline
 time.sleep(20)
for name in ['comparison.json','native-terminal.json','command.json','native-table.csv','native.log']:
 p=subprocess.run(['autor','cp',f'{node}:/root/sugarscape/{r.name}/{name}',str(r/name),'--json'],capture_output=True,text=True,timeout=120); (r/(name+'-download.json')).write_text(json.dumps({'exit_code':p.returncode,'stdout':p.stdout,'stderr':p.stderr},indent=2)+'\n'); assert p.returncode==0
result=json.loads((r/'comparison.json').read_text()); assert hashlib.sha256((r/'native-table.csv').read_bytes()).hexdigest()==result['native_table_sha256']
reference=r.parent/'brearcliffe-ec-ec-snapshot-001/readback/runs/released-code-pair-05-repeat-00/trajectory.csv'; assert hashlib.sha256(reference.read_bytes()).hexdigest()==result['trajectory_sha256']
with reference.open() as f: a=list(csv.DictReader(f))
lines=(r/'native-table.csv').read_text().splitlines(); index=next(i for i,row in enumerate(csv.reader(lines)) if row and row[0]=='[run number]'); b=list(csv.DictReader(lines[index:])); assert len(a)==len(b)==20001
for tick,(x,y) in enumerate(zip(a,b)):
 assert float(x['tick'])==float(y['[step]'])==tick
 for field in list(x)[1:]: assert math.isfinite(float(y[field])) and float(x[field])==float(y[field])
(r/'local-readback.json').write_text(json.dumps({'observations':20001,'fields':320016,'differences':0,'native_table_sha256':result['native_table_sha256'],'scope':'Fresh downloaded native table compared against previously audited local trajectory.'},indent=2)+'\n'); print('Full EC/EC native comparison and local readback passed',flush=True)
