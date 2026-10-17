"""Bounded diagnostic: record or replay native gmean outputs with exact input checks."""
import argparse,hashlib,json,os,platform,random,sys
from pathlib import Path
import numpy as np
p=argparse.ArgumentParser();p.add_argument('engine',type=Path);p.add_argument('library',type=Path);p.add_argument('output',type=Path);p.add_argument('--replay',type=Path);a=p.parse_args()
assert os.environ['PYTHONHASHSEED']=='0'
sys.path.insert(0,str(a.library.resolve()));sys.path.insert(0,str(a.engine.resolve()/'Common Resource- multi-level'))
from NetScape import NetScape
import NetAgent as N
import recorder
original=N.gmean
calls=[];observations=[]
a.output.mkdir(parents=True,exist_ok=False)
expected=[] if a.replay is None else json.loads(a.replay.read_text())
def observed(values):
 result=original(values)
 inputs=[float(v).hex() for v in values]
 if a.replay is not None:
  index=len(calls)
  assert index<len(expected)
  target=expected[index]
  if inputs!=target['inputs']:
   (a.output/'divergence.json').write_text(json.dumps({'call':index,'step':len(observations)+1,'inputs':inputs,'expected':target},indent=2)+'\n')
  assert inputs==target['inputs'],f'Input divergence at call {index}'
  result=np.float64(float.fromhex(target['result']))
 calls.append({'inputs':inputs,'result':float(result).hex()})
 return result
N.gmean=observed
np.random.seed(1);random.seed(1)
m=NetScape(seed=42)
for step in range(1,51):
 m.step()
 registry=m.ml.agents_by_type[N.NetAgent]
 observations.append({'step':step,'individual_agents':len(registry),'native_reporter':recorder.survivors(m),'agent_ids':sorted(x.unique_id for x in registry.values()),'retained_groups':len(m.ml.groups),'nested_group_edges':sum(child.type=='group' for group in m.ml.groups.values() for child in group.sub_agents.values())})
if a.replay is not None:assert len(calls)==len(expected)
(a.output/'calls.json').write_text(json.dumps(calls)+'\n')
(a.output/'observations.json').write_text(json.dumps(observations)+'\n')
(a.output/'prices.json').write_text(json.dumps(m.price_record)+'\n')
(a.output/'receipt.json').write_text(json.dumps({'steps':50,'calls':len(calls),'platform':platform.platform(),'replay':a.replay is not None,'source_sha256':hashlib.sha256(Path(N.__file__).read_bytes()).hexdigest(),'scope':'Causal diagnostic only; substituted outputs are never counted as native replication runs.'})+'\n')
print(json.dumps({'steps':50,'calls':len(calls)}))
