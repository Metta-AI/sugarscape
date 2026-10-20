"""Validate and summarize the predeclared ten-seed birth-threshold diagnostic."""
import argparse
import hashlib
import json
from pathlib import Path
from typing import Literal

import numpy as np
from pydantic import BaseModel, Field
from scipy.stats import t

class Completion(BaseModel):
    seed: int = Field(ge=101, le=110)
    variant: Literal['baseline', 'strict']
    command: list[str]
    elapsed_seconds: float = Field(gt=0)
    sha256: str = Field(pattern=r'^[0-9a-f]{64}$')

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('input', type=Path)
parser.add_argument('output', type=Path)
args = parser.parse_args()
assert not args.output.exists()
manifest = json.loads((args.input/'manifest.json').read_text())
assert manifest['seeds'] == list(range(101,111))
assert (manifest['infertility'], manifest['birth_cost'], manifest['cycles']) == (10,40,100000)
for name, digest in manifest['hashes'].items():
    assert hashlib.sha256((args.input/name).read_bytes()).hexdigest() == digest
records = [Completion.model_validate_json(line) for line in (args.input/'completed.jsonl').read_text().splitlines()]
assert [(r.seed,r.variant) for r in records] == [(seed,variant) for seed in range(101,111) for variant in ['baseline','strict']]
assert {p.name for p in args.input.glob('*.csv')} == {f'{r.variant}-{r.seed}.csv' for r in records}
metrics = ['population','wealth','mean_age','gini']
columns = ('cycle',*metrics,'landscape','births','deaths','growth','metabolism','death_loss','birth_loss','conservation_error')
rows = []
extinct = []
for record in records:
    path = args.input/f'{record.variant}-{record.seed}.csv'
    assert hashlib.sha256(path.read_bytes()).hexdigest() == record.sha256
    assert Path(record.command[0]).name == record.variant
    assert record.command[1:] == [str(record.seed),'10','40','100000']
    data = np.atleast_1d(np.genfromtxt(path,delimiter=',',names=True))
    assert data.dtype.names == columns
    assert all(np.isfinite(data[c]).all() for c in columns)
    final = int(data['cycle'][-1])
    assert 1 <= final <= 100000
    np.testing.assert_array_equal(data['cycle'],sorted({1,final,*range(100,final+1,100)}))
    for col in columns:
        if col not in ('mean_age','gini'):
            np.testing.assert_array_equal(data[col],np.floor(data[col]))
            assert (data[col]>=0).all()
    assert (data['population']<=2500).all() and (data['landscape']<=10000).all()
    assert ((data['gini']>=0)&(data['gini']<=1)).all() and (data['mean_age']>=0).all()
    assert (data['conservation_error']==0).all()
    assert final==100000 or data['population'][-1]==0
    row={'seed':record.seed,'variant':record.variant,'observations':len(data),'windows':{}}
    if data['population'][-1]==0:
        extinct.append([record.variant,record.seed])
    else:
        for label,start,stop in [('earlier',50000,75000),('later',75000,100000)]:
            mask=(data['cycle']>start)&(data['cycle']<=stop)
            assert mask.sum()==250
            row['windows'][label]={metric:float(data[metric][mask].mean()) for metric in metrics}
    rows.append(row)
summary={'validated_runs':len(rows),'observations':sum(r['observations'] for r in rows),'extinct':extinct,'per_seed':rows,'statistics':{},'interpretation':'Exploratory sensitivity; not evidence identifying the author rule. All seeds retained.'}
if not extinct:
    for metric in metrics:
        summary['statistics'][metric]={}
        for window in ['earlier','later']:
            values={v:np.array([r['windows'][window][metric] for r in rows if r['variant']==v]) for v in ['baseline','strict']}
            values['strict_minus_baseline']=values['strict']-values['baseline']
            summary['statistics'][metric][window]={}
            for variant,array in values.items():
                mean=float(array.mean())
                sd=float(array.std(ddof=1))
                half=float(t.ppf(.975,9))*sd/np.sqrt(10)
                summary['statistics'][metric][window][variant]={'mean':mean,'sd':sd,'ci95':[mean-half,mean+half]}
args.output.mkdir(parents=True)
(args.output/'analysis.json').write_text(json.dumps(summary,indent=2,allow_nan=False)+'\n')
print(json.dumps({k:summary[k] for k in ['validated_runs','observations','extinct','statistics']},indent=2))
