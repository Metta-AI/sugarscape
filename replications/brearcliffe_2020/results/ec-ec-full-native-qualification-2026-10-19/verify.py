from pathlib import Path
import csv,json,hashlib,subprocess,time,math
root=Path(__file__).resolve().parent
reference=Path('/root/sugarscape/brearcliffe-existing-host-ensemble-001/batch/runs/released-code-pair-05-repeat-00')
model=reference/'model.nlogo'
assert hashlib.sha256(model.read_bytes()).hexdigest()=='70031804e9e2db5c47b533fac45da1a755c2291cb5b5a911736172399f48da67'
assert hashlib.sha256((reference/'trajectory.csv').read_bytes()).hexdigest()=='f44f53583f491a40307de1725d60b4c0d93db03e5940a82492b8424f96eb64c5'
command=['/usr/bin/java','-Xmx1g','-Djava.awt.headless=true','-cp','/root/sugarscape/brearcliffe-existing-host-qualification-001/payload/app/*','org.nlogo.headless.Main','--model',str(model),'--setup-file',str(root/'experiment.xml'),'--experiment','recorder-qualification','--table',str(root/'native-table.csv'),'--threads','1']
(root/'command.json').write_text(json.dumps(command,indent=2)+chr(10))
start=time.monotonic()
with (root/'native.log').open('x') as log:
 p=subprocess.run(command,cwd=reference,stdout=log,stderr=subprocess.STDOUT,timeout=600)
(root/'native-terminal.json').write_text(json.dumps({'exit_code':p.returncode,'elapsed_seconds':time.monotonic()-start},indent=2)+chr(10)); assert p.returncode==0
with (reference/'trajectory.csv').open() as f: recorded=list(csv.DictReader(f))
lines=(root/'native-table.csv').read_text().splitlines(); index=next(i for i,row in enumerate(csv.reader(lines)) if row and row[0]=='[run number]'); native=list(csv.DictReader(lines[index:])); assert len(native)==len(recorded)==20001
fields=list(recorded[0])[1:]; assert fields==next(csv.reader([lines[index]]))[10:]
for tick,(a,b) in enumerate(zip(recorded,native)):
 assert float(a['tick'])==float(b['[step]'])==tick
 for field in fields:
  x,y=float(a[field]),float(b[field]); assert math.isfinite(x) and math.isfinite(y) and x==y,(tick,field,x,y)
result={'seed':381016329,'pairing':['EC','EC'],'observations':20001,'compared_fields':320016,'differences':0,'trajectory_sha256':hashlib.sha256((reference/'trajectory.csv').read_bytes()).hexdigest(),'native_table_sha256':hashlib.sha256((root/'native-table.csv').read_bytes()).hexdigest(),'scope':'Full-horizon native BehaviorSpace versus existing custom recorder, one original input. No new seed coverage or paper verdict.'}
(root/'comparison.json').write_text(json.dumps(result,indent=2)+chr(10)); print(json.dumps(result))
