"""Trace unchanged native gmean calls during one full model step; never counts as ensemble coverage."""
import argparse,hashlib,inspect,json,os,platform,random,sys
from pathlib import Path
import numpy as np
import scipy
import scipy.stats.mstats as stats
import mesa,networkx
p=argparse.ArgumentParser();p.add_argument('engine',type=Path);p.add_argument('library',type=Path);p.add_argument('output',type=Path);a=p.parse_args()
assert os.environ['PYTHONHASHSEED']=='0'
sys.path.insert(0,str(a.library.resolve()));sys.path.insert(0,str(a.engine.resolve()/'Common Resource- multi-level'))
from NetScape import NetScape
import NetAgent as N
original=N.gmean
calls=[]
def observed(values):
 result=original(values)
 data=np.asarray(values)
 logs=np.log(data)
 calls.append({'inputs':[float(v).hex() for v in values],'logs':[float(v).hex() for v in logs],'mean_log':float(np.mean(logs)).hex(),'result':float(result).hex()})
 return result
N.gmean=observed
np.random.seed(1);random.seed(1)
m=NetScape(seed=42);m.step()
a.output.mkdir(parents=True,exist_ok=False)
(a.output/'trace.json').write_text(json.dumps({'python':platform.python_version(),'platform':platform.platform(),'numpy':np.__version__,'scipy':scipy.__version__,'mesa':mesa.__version__,'networkx':networkx.__version__,'gmean_sha256':hashlib.sha256(inspect.getsource(original).encode()).hexdigest(),'native_agent_sha256':hashlib.sha256(Path(N.__file__).read_bytes()).hexdigest(),'steps':1,'calls':calls},indent=2)+'\n')
(a.output/'prices.json').write_text(json.dumps(m.price_record))
print(json.dumps({'calls':len(calls),'prices':len(m.price_record[1])}))
