"""Independently audit complete or explicitly partial elite/founder observations."""
import argparse
import gzip
import hashlib
import io
import json
from pathlib import Path

import numpy as np
import pandas as pd

parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('run',type=Path)
parser.add_argument('mode',choices=['prefix','complete'])
parser.add_argument('output',type=Path)
args=parser.parse_args()
root=Path(__file__).resolve().parent
manifest=json.loads((args.run/'manifest.json').read_text())
assert manifest['cycles']==50000 and manifest['record_every']==100 and manifest['seeds']==list(range(1,101))
for key,name in [('source_sha256','simulate.cpp'),('protocol_sha256','OBSERVATION_PROTOCOL.md'),('runner_sha256','run_observations.py')]:
    assert hashlib.sha256((root/name).read_bytes()).hexdigest()==manifest[key]
ledger=(args.run/'completed.jsonl').read_bytes()
assert ledger.endswith(b'\n')
records=[json.loads(line) for line in ledger.splitlines()]
expected=[(scenario,seed) for scenario in ['low-fertility','birth-cost'] for seed in range(1,101)]
assert [(row['scenario'],row['seed']) for row in records]==expected[:len(records)]
assert 0<len(records)<=200
if args.mode=='complete': assert len(records)==200,'All 200 declared runs are required'
cycles=np.array([1,*range(100,50001,100)])
per_run=[]
for record in records:
    scenario,seed=record['scenario'],record['seed']
    assert record['exit_code']==0 and record['prior_prefix_byte_identical']
    assert json.loads((args.run/f'{scenario}-{seed}-exit.json').read_text())['exit_code']==0
    frames={}
    for label,name in [('aggregate',f'{scenario}-{seed}.csv'),('observations',f'{scenario}-{seed}-observations.csv')]:
        raw=gzip.decompress((args.run/(name+'.gz')).read_bytes())
        assert hashlib.sha256(raw).hexdigest()==record['raw_sha256'][name]
        assert (args.run/name).read_bytes()==raw
        frames[label]=pd.read_csv(io.BytesIO(raw))
    aggregate,observations=frames['aggregate'],frames['observations']
    assert len(aggregate)==501 and len(observations)==record['observation_rows']
    assert np.array_equal(aggregate.cycle,cycles)
    assert np.isfinite(aggregate.to_numpy()).all() and aggregate.conservation_error.eq(0).all()
    prior=root/'results'/f'{scenario}-ensemble-2026-10-15'/f'seed-{seed}.csv.gz'
    original=gzip.decompress(prior.read_bytes()).splitlines(keepends=True)
    prefix=original[0]+b''.join(line for line in original[1:] if int(line.split(b',')[0])<=50000)
    assert prefix==(args.run/f'{scenario}-{seed}.csv').read_bytes()
    assert set(observations.kind)=={'elite','founder'}
    assert np.isfinite(observations.select_dtypes(include='number').to_numpy()).all()
    assert set(observations.cycle)==set(cycles)
    assert observations.wealth.ge(0).all() and observations.mean_age.ge(0).all()
    assert observations.mean_age.le(observations.cycle).all()
    elite=observations[observations.kind=='elite'].set_index('cycle')
    assert len(elite)==501 and np.array_equal(elite.index,cycles)
    assert elite.agent_id.eq(-1).all()
    assert np.array_equal(elite['count'],(aggregate.population.to_numpy()+9)//10)
    assert (elite.wealth.to_numpy()<=aggregate.wealth.to_numpy()).all()
    founders=observations[observations.kind=='founder']
    assert founders['count'].eq(1).all() and founders.agent_id.between(0,29).all()
    assert not founders.duplicated(['cycle','agent_id']).any()
    birth_cycles={}
    for identifier,group in founders.groupby('agent_id'):
        assert np.array_equal(group.cycle,cycles[(cycles>=group.cycle.min())&(cycles<=group.cycle.max())])
        born=group.cycle-group.mean_age
        assert born.nunique()==1 and float(born.iloc[0]).is_integer()
        birth_cycles[str(int(identifier))]=int(born.iloc[0])
    earlier_complete_checks=0
    for cycle,group in founders.groupby('cycle'):
        population=int(aggregate.loc[aggregate.cycle==cycle,'population'].iloc[0])
        assert len(group)<=population
        if len(group)==population:
            selected=group.sort_values(['wealth','agent_id'],ascending=[False,True]).head((population+9)//10)
            assert selected.wealth.sum()==elite.loc[cycle,'wealth']
            assert np.isclose(selected.mean_age.mean(),elite.loc[cycle,'mean_age'],atol=1e-12,rtol=1e-12)
            earlier_complete_checks+=1
    window=(elite.index>35000)&(elite.index<=50000)
    per_run.append({'scenario':scenario,'seed':seed,'aggregate_rows':501,'founder_rows':len(founders),
                    'elite_rows':501,'independent_early_elite_checks':earlier_complete_checks,
                    'founder_birth_cycles':birth_cycles,
                    'late_elite_mean_age':float(elite.loc[window,'mean_age'].mean()),
                    'late_elite_mean_wealth':float(elite.loc[window,'wealth'].mean()),
                    'founders_alive_at_50000':sorted(map(int,founders.loc[founders.cycle==50000,'agent_id']))})
report={'mode':args.mode,'completed_ensemble':args.mode=='complete','validated_runs':len(records),'required_runs':200,
        'manifest_sha256':hashlib.sha256((args.run/'manifest.json').read_bytes()).hexdigest(),
        'ledger_snapshot_sha256':hashlib.sha256(ledger).hexdigest(),'per_run':per_run,
        'scope':'Exact prior aggregate prefix verification, founder continuity, and early complete-population elite checks. Later elite rank selection has no independent full-state oracle. No historical source-equivalence or paper verdict.'}
args.output.mkdir(parents=True,exist_ok=False)
(args.output/'ledger-snapshot.jsonl').write_bytes(ledger)
(args.output/'audit.json').write_text(json.dumps(report,indent=2,allow_nan=False)+'\n')
print(json.dumps({'mode':args.mode,'validated_runs':len(records),'complete':report['completed_ensemble']}))
