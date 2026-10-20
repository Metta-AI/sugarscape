from pathlib import Path
import csv,gzip,hashlib,json
import numpy as np
root=Path(__file__).resolve().parent
source=root.parent/'brearcliffe-ec-ec-snapshot-001'
audit=json.loads((source/'union-audit/audit.json').read_text())
runs=sorted((source/'readback/runs').iterdir()); assert len(runs)==50
matrix=[]; pins={}
for run in runs:
 p=run/'trajectory.csv'; b=p.read_bytes(); sha=hashlib.sha256(b).hexdigest(); pins[run.name]=sha
 with p.open() as f:
  rows=csv.DictReader(f); fields=rows.fieldnames
  for row in rows: pass
 assert int(row['tick'])==20000
 matrix.append([float(row[k]) for k in fields[3:]])
a=np.array(matrix); assert a.shape==(50,14)
indices=np.frombuffer(gzip.decompress((source/'cohort/bootstrap-indices.u8.gz').read_bytes()),dtype=np.uint8).reshape(20000,50)
contrasts=a[:,::2]-a[:,1::2]; pooled=(a[:,::2]+a[:,1::2])/2
with (root/'paired-endpoints.csv').open('w') as f:
 w=csv.writer(f); w.writerow(['run_id']+fields[3:]); w.writerows([[r.name,*x] for r,x in zip(runs,a)])
records=[]
for j in range(7):
 x=contrasts[:,j]; draws=x[indices].mean(axis=1); lo,hi=np.quantile(draws,[.025,.975],method='linear')
 records.append({'A_metric':fields[3+2*j],'B_metric':fields[4+2*j],'A_minus_B_mean':float(x.mean()),'paired_sample_sd':float(x.std(ddof=1)),'pointwise_bootstrap_interval_95':[float(lo),float(hi)],'A_greater_runs':int((x>0).sum()),'equal_runs':int((x==0).sum()),'A_less_runs':int((x<0).sum()),'pooled_breed_mean':float(pooled[:,j].mean())})
report={'runs':50,'bootstrap_repetitions':20000,'trajectory_sha256':pins,'records':records,'scope':'Exploratory paired endpoint contrasts selected after the discrepancy. Existing whole-run draws, pointwise intervals only; not paper sampling uncertainty, simultaneous inference, or a negative replication verdict.'}
(root/'contrasts.json').write_text(json.dumps(report,indent=2)+'\n'); print(json.dumps(records,indent=2))
