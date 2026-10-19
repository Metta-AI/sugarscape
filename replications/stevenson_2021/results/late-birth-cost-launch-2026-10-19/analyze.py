import argparse,csv,gzip,hashlib,io,json
from pathlib import Path
import numpy as np
from scipy.stats import t
parser=argparse.ArgumentParser()
parser.add_argument('run',type=Path)
parser.add_argument('output',type=Path)
args=parser.parse_args()
protocol=json.loads((args.run/'protocol.json').read_text())
assert protocol['seeds']==list(range(1,101)) and protocol['windows']==[[75000,100000],[130000,150000]]
assert (protocol['infertility'],protocol['birth_cost'],protocol['cycles'],protocol['record_every'])==(10,40,150000,100)
for name,key in [('simulate.cpp','source_sha256'),('simulate','binary_sha256'),('run.py','runner_sha256')]:
 assert hashlib.sha256((args.run/name).read_bytes()).hexdigest()==protocol[key]
records=[json.loads(x) for x in (args.run/'completed.jsonl').read_text().splitlines()]
assert [r['seed'] for r in records]==list(range(1,101)), 'Require all 100 completed seeds'
assert not args.output.exists()
prior=Path('/Users/relh/Code/workspace/sugarscape-stevenson/replications/stevenson_2021/results/birth-cost-ensemble-2026-10-15')
old={x['seed']:x for x in map(json.loads,(prior/'completed.jsonl').read_text().splitlines())}
metrics=['population','wealth','mean_age','gini']
values=[]
for record in records:
 seed=record['seed'];assert record['exit_code']==0
 raw=(args.run/f'seed-{seed}.csv').read_bytes()
 assert hashlib.sha256(raw).hexdigest()==record['trajectory_sha256']
 original=gzip.decompress((prior/f'seed-{seed}.csv.gz').read_bytes())
 assert hashlib.sha256(original).hexdigest()==old[seed]['trajectory_sha256']
 assert b''.join(raw.splitlines(keepends=True)[:len(original.splitlines())])==original
 rows=list(csv.DictReader(io.StringIO(raw.decode())))
 assert [int(r['cycle']) for r in rows]==[1]+list(range(100,150001,100))
 assert all(float(r['conservation_error'])==0 and 0<float(r['population'])<=2500 for r in rows)
 assert np.isfinite([[float(v) for v in r.values()] for r in rows]).all()
 for start,end in protocol['windows']:
  subset=[r for r in rows if start<int(r['cycle'])<=end]
  assert len(subset)==(end-start)//100
  values.append(dict(seed=seed,start=start,end=end,**{m:float(np.mean([float(r[m]) for r in subset])) for m in metrics}))
summary=[]
for metric in metrics:
 early=np.array([r[metric] for r in values if r['end']==100000])
 late=np.array([r[metric] for r in values if r['end']==150000])
 for label,x in [('early',early),('late',late),('paired_late_minus_early',late-early)]:
  mean=float(x.mean());sd=float(x.std(ddof=1));half=float(t.ppf(.975,99)*sd/10)
  summary.append(dict(metric=metric,window=label,mean=mean,sd=sd,ci95=[mean-half,mean+half]))
args.output.mkdir()
with (args.output/'seed-means.csv').open('w') as output:
 writer=csv.DictWriter(output,fieldnames=list(values[0]));writer.writeheader();writer.writerows(values)
(args.output/'summary.json').write_text(json.dumps(dict(completed_seeds=100,observations=150100,exact_prefix_observations=100100,summary=summary,scope='Descriptive late-window sensitivity, no inferred target-paper sampling or completion.'),indent=2)+'\n')
print(json.dumps(summary,indent=2))
