import hashlib,json,platform,sys,time
from pathlib import Path
import mesa,numpy as np,networkx
sys.path.insert(0,"/Users/relh/Code/workspace/sugarscape-pike-library-reference")
root=Path('/Users/relh/Code/workspace/sugarscape-pike-reference/Initial/NetScape_Brute')
sys.path.insert(0,str(root))
from NetScape import NetScape
import recorder
import NetAgent as N
import csv
out=Path(__file__).parent
(out/'manifest.json').write_text(json.dumps({'python':platform.python_version(),'mesa':mesa.__version__,'numpy':np.__version__,'networkx':networkx.__version__,'library_revision':'99d2091721076df9fff32e8b49a0e33e98c34a6f','revision':'585e53398f4f58e89ec184c83bb20819f0e4c96a','source_hashes':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in root.glob('*.py')},'numpy_seed':0,'mesa_seed':42,'steps':1000},indent=2))
np.random.seed(0)
m=NetScape(seed=42)
started=time.monotonic()
observed=[]
registry=m.ml.agents_by_type[N.NetAgent]
assert len(registry)==200
initial=[{'id':a.unique_id,'position':a.pos,'accumulations':a.accumulations,'metabolism':{k:int(v) for k,v in a.metabolism.items()}} for a in registry.values()]
(out/'initial-agents.json').write_text(json.dumps(initial))
for i in range(1000):
 m.step()
 registry=m.ml.agents_by_type[N.NetAgent]
 ids=sorted(a.unique_id for a in registry.values())
 assert len(ids)==len(set(ids)) and 0 <= len(ids) <= 200
 observed.append({'step':i+1,'individual_agents':len(ids),'native_reporter':recorder.survivors(m),'agent_ids':ids})
 if i%100==99: print(i+1,recorder.survivors(m),flush=True)
(out/'prices.json').write_text(json.dumps(m.price_record))
m.datacollector.get_model_vars_dataframe().to_csv(out/'population.csv',index=False)

(out/'observations.json').write_text(json.dumps(observed))
m.datacollector.get_table_dataframe('Health').to_csv(out/'health.csv',index=False)

(out/'complete.json').write_text(json.dumps({'steps':1000,'survivors':recorder.survivors(m),'elapsed':time.monotonic()-started}))
