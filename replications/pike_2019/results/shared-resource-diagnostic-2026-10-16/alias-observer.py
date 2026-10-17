import hashlib,json,platform,sys,time,random,os
from pathlib import Path
import mesa,numpy as np,networkx
sys.path.insert(0,"/Users/relh/Code/workspace/sugarscape-pike-library-reference")
root=Path('/Users/relh/Code/workspace/sugarscape-pike-reference/Common Resource- multi-level')
sys.path.insert(0,str(root))
from NetScape import NetScape
import recorder
import math
import organization
from collections import Counter
original_calc=organization.rules.calc_accumulations
branch_counts=Counter()
branch_samples=[]
alias_samples=[]
def observed_calc(self,meta):
 result=original_calc(self,meta)
 branch_counts['calls']+=1
 direct=[a for a in meta.sub_agents.values() if a.type=='agent']
 unique={id(a.accumulations):a.accumulations for a in direct}
 branch_counts['calls_with_shared_holding_objects']+=len(unique)<len(direct)
 if len(unique)<len(direct) and len(alias_samples)<10 and all(math.isfinite(float(v)) for v in result.values()):
  alias_samples.append({'step':meta.model.step_num,'group_id':meta.unique_id,'direct_agents':len(direct),'distinct_holding_objects':len(unique),'native_sum':result,'sum_each_holding_object_once':{str(k):sum(v[k] for v in unique.values()) for k in [1.0,2.0]}})
 nested=[a for a in meta.sub_agents.values() if a.type=='group']
 branch_counts['calls_with_nested_groups']+=bool(nested)
 branch_counts['nested_child_occurrences']+=len(nested)
 branch_counts['legacy_meta_child_occurrences']+=sum(a.type=='meta' for a in meta.sub_agents.values())
 if nested and len(branch_samples)<10:
  branch_samples.append(json.loads(json.dumps({'step':meta.model.step_num,'group_id':meta.unique_id,'returned_accumulations':result,'children':[{'id':a.unique_id,'type':a.type,'policy_accumulations':a.policy.accumulations} for a in nested[:5]]})))
 return result
organization.rules.calc_accumulations=observed_calc
import NetAgent as N
import csv
out=Path(__file__).parent
(out/'manifest.json').write_text(json.dumps({'python':platform.python_version(),'mesa':mesa.__version__,'numpy':np.__version__,'networkx':networkx.__version__,'library_revision':'99d2091721076df9fff32e8b49a0e33e98c34a6f','revision':'585e53398f4f58e89ec184c83bb20819f0e4c96a','source_hashes':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in root.glob('*.py')},'numpy_seed':0,'policy_random_seed':0,'pythonhashseed':os.environ['PYTHONHASHSEED'],'variant':'common-multi','mesa_seed':42,'steps':1000},indent=2))
np.random.seed(0)
random.seed(0)
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

(out/'branch-audit.json').write_text(json.dumps({'counts':dict(branch_counts),'first_nested_samples':branch_samples,'first_shared_holding_samples':alias_samples,'scope':'Passive observations; repeated child occurrences are not independent or net resource losses.'},indent=2))
(out/'complete.json').write_text(json.dumps({'steps':1000,'native_reporter':recorder.survivors(m),'individual_agents':len(registry),'elapsed':time.monotonic()-started}))
