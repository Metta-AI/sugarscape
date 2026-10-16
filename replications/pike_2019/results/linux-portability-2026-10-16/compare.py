from pathlib import Path
import csv, hashlib, json, math
root=Path('/Users/relh/Code/workspace/sugarscape-replication-evidence')
cloud=root/'pike-cloud-portability-001/download-repaired-001'
rows=[]
for phase in range(1,4):
    local=root/f'pike-segment-phase{phase}-003'
    for health in sorted(local.rglob('health.csv')):
        for name in ['health.csv','population.csv','prices.json','initial-agents.json','observations.json']:
            a=health.parent/name
            b=cloud/f'phase{phase}'/a.relative_to(local)
            if name.endswith('.csv'):
                av=list(csv.reader(a.open()));bv=list(csv.reader(b.open()))
            else:
                av=json.loads(a.read_text());bv=json.loads(b.read_text())
            pending=[(av,bv)];count=0;diffs=[]
            while pending:
                x,y=pending.pop()
                assert type(x)==type(y)
                if isinstance(x,dict):
                    assert x.keys()==y.keys();pending.extend((x[k],y[k]) for k in x)
                elif isinstance(x,list):
                    assert len(x)==len(y);pending.extend(zip(x,y))
                elif x!=y:
                    xx,yy=float(x),float(y)
                    assert math.isfinite(xx) and math.isfinite(yy)
                    diffs.append(abs(xx-yy))
                else:
                    count+=1
            rows.append({'phase':phase,'file':str(a.relative_to(local)),'local_sha256':hashlib.sha256(a.read_bytes()).hexdigest(),'cloud_sha256':hashlib.sha256(b.read_bytes()).hexdigest(),'equal_leaves':count,'different_numeric_leaves':len(diffs),'max_absolute_difference':max(diffs,default=0)})
report={'files':rows,'scope':'Three duplicate conditions, no added coverage. Numeric differences reported without assuming tolerance.'}
(root/'pike-cloud-portability-001/comparison.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
