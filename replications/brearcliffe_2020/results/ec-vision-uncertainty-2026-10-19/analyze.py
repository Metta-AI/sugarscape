from pathlib import Path
import csv,gzip,hashlib,json
import numpy as np
r=Path(__file__).resolve().parent
repo=Path('/Users/relh/Code/workspace/sugarscape-brearcliffe/replications/brearcliffe_2020')
source=r.parent/'brearcliffe-rule-m-ec-snapshot-001/cohort'
protocol={'scope':'Exploratory diagnosis selected after observing EC vision mismatch; not a confirmatory acceptance rule.', 'metric':'mean [vision] of group-B','pair_index':1,'runs':50,'columns':286,'resamples':20000,'resampling_unit':'whole run, same retained draws as prior cohort analysis','band':'Mean plus/minus the 0.95 type7 quantile of the maximum absolute bootstrap deviation standardized by the original standard error over 286 column centers. Fixed standard errors, not bootstrap-t.', 'limits':['Approximate bootstrap band for our mean curve, not a confidence band for the historical paper.', 'Selected metric after inspection; no simultaneous guarantee across other metrics or cohorts.', 'Comparison uses column centers and vertical raster bounds; not the previous horizontal-window range statistic.', 'Overlap does not establish equivalence; no posthoc change to replication criteria.']}
(r/'protocol.json').write_text(json.dumps(protocol,indent=2)+'\n')
summary=json.loads((source/'summary.json').read_text())
audit=json.loads((r.parent/'brearcliffe-rule-m-sarsa-snapshot-001/union-audit/audit.json').read_text())
by_id={x['run_id']:x for x in audit['completed']}
curves=json.load(gzip.open(repo/'results/horizontal-calibration-correction-2026-10-19/rule-m-ec/curve-comparison.json.gz','rt'))
rows=[x for x in curves['records'] if x['figure']==4 and x['breed']=='B']
assert len(rows)==286 and [x['column'] for x in rows]==list(range(17,303))
assert all('metric_interval' in x for x in rows)
ticks=np.arange(286)*20000/285
values=[]; pins=[]
for run_id in sorted(summary['trajectory_sha256']):
 item=by_id[run_id]; p=Path(item['directory'])/'trajectory.csv'
 assert hashlib.sha256(p.read_bytes()).hexdigest()==summary['trajectory_sha256'][run_id]==item['trajectory_sha256']
 with p.open() as f:
  trajectory=list(csv.DictReader(f))
 assert len(trajectory)==20001 and all(float(x['tick'])==i for i,x in enumerate(trajectory))
 v=np.array([float(x[protocol['metric']]) for x in trajectory]); assert np.all(np.isfinite(v))
 values.append(np.interp(ticks,np.arange(20001),v))
 pins.append({'run_id':run_id,'path':str(p),'sha256':item['trajectory_sha256']})
x=np.array(values); assert x.shape==(50,286)
indices_bytes=gzip.decompress((source/'bootstrap-indices.u8.gz').read_bytes())
assert hashlib.sha256(indices_bytes).hexdigest()==summary['bootstrap']['indices_sha256']
indices=np.frombuffer(indices_bytes,dtype=np.uint8).reshape(20000,50)
assert np.all(indices<50)
counts=np.zeros((20000,50)); np.add.at(counts,(np.repeat(np.arange(20000),50),indices.ravel()),1)
mean=x.mean(axis=0); se=x.std(axis=0,ddof=1)/np.sqrt(50); assert np.all(se>0)
boot=counts@x/50
maxima=np.max(np.abs(boot-mean)/se,axis=1)
critical=float(np.quantile(maxima,.95,method='linear')); lower=mean-critical*se; upper=mean+critical*se
paper=np.array([y['metric_interval'] for y in rows]); overlap=(upper>=paper[:,0])&(lower<=paper[:,1])
np.savetxt(r/'input-matrix.csv',x,delimiter=','); np.savetxt(r/'ticks.csv',ticks,delimiter=',')
np.savetxt(r/'bootstrap-maxima.csv',maxima,delimiter=',')
with (r/'bands.csv').open('w') as f:
 writer=csv.writer(f); writer.writerow(['column','tick','mean','standard_error','lower','upper','paper_lower','paper_upper','overlap'])
 writer.writerows((row['column'],ticks[i],mean[i],se[i],lower[i],upper[i],*paper[i],int(overlap[i])) for i,row in enumerate(rows))
(r/'sources.json').write_text(json.dumps({'trajectories':pins,'bootstrap':str(source/'bootstrap-indices.u8.gz'),'bootstrap_uncompressed_sha256':summary['bootstrap']['indices_sha256']},indent=2)+'\n')
report={'runs':50,'columns':286,'resamples':20000,'critical':critical,'band_raster_overlaps':int(overlap.sum()),'mean_above_at_column_center':int((mean>paper[:,1]).sum()),'max_mean_above':float(np.max(mean-paper[:,1])),'numpy_version':np.__version__,'scope':'Exploratory uncertainty diagnostic; no replication verdict or added coverage.'}
(r/'summary.json').write_text(json.dumps(report,indent=2)+'\n'); print(json.dumps(report,indent=2))
