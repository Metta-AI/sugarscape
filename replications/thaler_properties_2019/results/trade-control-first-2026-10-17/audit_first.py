"""Audit the two complete native control trajectories and their paired initialization."""
import csv
import gzip
import hashlib
import json
import math
from pathlib import Path

assets=Path(__file__).resolve().parent
root=assets.parent/'thaler-local-linux-001/home/sugarscape/thaler-properties-trade-control-001/first'
protocol=json.loads((assets/'protocol.json').read_text())
manifest=json.loads((root/'manifest.json').read_text())
assert manifest['protocol']==protocol and manifest['interval']==[0,1]
assert json.loads((root/'complete.json').read_text())=={'completed_runs':2}
assert hashlib.sha256((root/'run_observer_ensemble.py').read_bytes()).hexdigest()==manifest['runner_sha256']
records=[json.loads(line) for line in (root/'completed.jsonl').read_text().splitlines()]
assert [r['scenario'] for r in records]==['trade_off','trade_on']
initial={};cases=[];texts=[]
for record,scenario in zip(records,protocol['scenarios']):
    assert record['index']==0 and record['seed']==protocol['seeds'][0] and record['steps']==1000
    folder=root/record['scenario']/f"000-{record['seed']}"
    for name,digest in record['files_sha256'].items():assert hashlib.sha256((folder/name).read_bytes()).hexdigest()==digest
    for kind in ['summary','agents','trades','cells']:
        assert gzip.decompress((folder/f'trajectory.{kind}.csv.gz').read_bytes())==(folder/f'trajectory.{kind}.csv').read_bytes()
    command=json.loads((folder/'command.json').read_text())
    assert command[:5]==[protocol['variants']['original']['root']+'/observe',scenario['constructor'],str(record['seed']),'1000','10']
    summaries=list(csv.DictReader((folder/'trajectory.summary.csv').open()))
    assert [int(r['time']) for r in summaries]==list(range(1001))
    assert all(math.isfinite(float(v)) for r in summaries for v in r.values())
    agents={t:[] for t in range(0,1001,10)}
    for r in csv.DictReader((folder/'trajectory.agents.csv').open()):
        agents[int(r['time'])].append(r)
        assert all(math.isfinite(float(v)) for k,v in r.items() if k!='culture')
    trades={t:[] for t in agents}
    for r in csv.DictReader((folder/'trajectory.trades.csv').open()):
        trades[int(r['time'])].append(r)
        assert all(math.isfinite(float(v)) for v in r.values())
    for t,group in agents.items():
        assert len(group)==int(summaries[t]['population'])==len({r['id'] for r in group})
        assert len(trades[t])==int(summaries[t]['trade_count'])
        for field in ['sugar','spice']:
            assert math.isclose(sum(float(r[field]) for r in group),float(summaries[t]['agent_'+field]),rel_tol=1e-12,abs_tol=1e-9)
    cells=list(csv.DictReader((folder/'trajectory.cells.csv').open()))
    initial[record['scenario']]={'agents':agents[0],'cells':[r for r in cells if r['time']=='0'],'summary':summaries[0]}
    texts.append((folder/'trajectory.scenario.txt').read_text().splitlines())
    cases.append({'scenario':record['scenario'],'horizon':1000,'snapshot_agent_observations':sum(map(len,agents.values())),'snapshot_trade_records':sum(map(len,trades.values())),'final_population':int(summaries[-1]['population'])})
assert initial['trade_off']==initial['trade_on']
differences=[{'line':i+1,'off':a,'on':b} for i,(a,b) in enumerate(zip(*texts)) if a!=b]
assert len(texts[0])==len(texts[1]) and len(differences)==3
assert differences[0]['off'].startswith('Constructor:') and differences[1]['off'].startswith('Scenario:')
assert differences[2]['off'].startswith('T rule active (trading):')
assert differences[2]['off'].endswith('False') and differences[2]['on'].endswith('True')
report={'cases':cases,'initial_agents_cells_summary_exact':True,'resolved_scenario_differences':differences,'source_files_pinned':len(protocol['variants']['original']['source_sha256']),'scope':'Two complete first-seed workflows; initialization and sole treatment toggle verified. No ensemble or paper-level claim.'}
with (assets/'first-audit.json').open('x') as stream:stream.write(json.dumps(report,indent=2)+'\n')
print(json.dumps(report))
