"""Run the unmodified released parser over exact native JSON byte streams."""
from concurrent.futures import ThreadPoolExecutor
import gzip
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import numpy as np

root = Path(__file__).parent.resolve()
source = root.parent / 'blueprints-bentham-timeseries-001'
engine = Path('/Users/relh/Code/workspace/sugarscape-dtl-blueprints-reference')
parser = engine / 'plots/plot.py'
pinned = subprocess.check_output(['git','show','b9ca671ab7591c7b3606f2d76c33eda344d626d1:plots/plot.py'],cwd=engine)
assert parser.read_bytes() == pinned
pins = json.loads((source / 'provenance.json').read_text())['files']
for name in ['inputs.json','independent-means.csv']:
    assert hashlib.sha256((source / name).read_bytes()).hexdigest() == pins[name]
inputs = json.loads((source / 'inputs.json').read_text())
assert len(inputs) == 500
pipes = root / 'native-inputs'
pipes.mkdir()
for seed in inputs:
    os.mkfifo(pipes / f'benthamHalfLookaheadBinary{seed}.json')
config = {'dataCollectionOptions':{'plotTimesteps':5000,'decisionModels':['benthamHalfLookaheadBinary'],'plots':[]}}
(root / 'plot-config.json').write_text(json.dumps(config)+'\n')
command = [sys.executable,str(parser),'--path',str(pipes)+'/', '--conf',str(root/'plot-config.json'),'--outf',str(root/'author-means.dat')]
(root / 'command.json').write_text(json.dumps(command,indent=2)+'\n')

def supply(seed, item):
    """Send one complete verified native trajectory when the parser opens it."""
    with (pipes / f'benthamHalfLookaheadBinary{seed}.json').open('wb') as stream:
        raw = gzip.decompress(Path(item['path']).read_bytes())
        digest = hashlib.sha256(raw).hexdigest()
        assert digest == item['record']['trajectory_sha256']
        written = stream.write(raw)
        assert written == len(raw)
    return {'seed':int(seed),'bytes':written,'sha256':digest}

order = os.listdir(os.fsencode(str(pipes) + '/'))
(root/'directory-order.json').write_text(json.dumps([os.fsdecode(name) for name in order],indent=2)+'\n')

def supply_directory():
    """Feed the frozen directory in its native enumeration order."""
    return [supply(os.fsdecode(name).removeprefix('benthamHalfLookaheadBinary').removesuffix('.json'), inputs[os.fsdecode(name).removeprefix('benthamHalfLookaheadBinary').removesuffix('.json')]) for name in order]

assert os.listdir(os.fsencode(str(pipes) + '/')) == order
with ThreadPoolExecutor(max_workers=1) as executor:
    future = executor.submit(supply_directory)
    with (root/'author-stdout.log').open('wb') as stdout, (root/'author-stderr.log').open('wb') as stderr:
        subprocess.run(command,cwd=root,stdout=stdout,stderr=stderr,timeout=600,check=True)
    supplied = future.result(timeout=10)
assert len(supplied) == 500
(root/'supplied.json').write_text(json.dumps(supplied,indent=2)+'\n')
author = np.loadtxt(root/'author-means.dat',skiprows=1)
independent = np.loadtxt(source/'independent-means.csv',delimiter=',',skiprows=1)
assert author.shape == independent.shape == (5001,7)
assert np.array_equal(author[:,:2],independent[:,:2])
assert np.allclose(author[:,1:],independent[:,1:],rtol=1e-12,atol=1e-8)
report = {'runs':500,'observations':2500500,'compared_values':30006,'population_exact':True,'rtol':1e-12,'atol':1e-8,'max_absolute_errors':np.max(np.abs(author[:,1:]-independent[:,1:]),axis=0).tolist(),'parser_sha256':hashlib.sha256(pinned).hexdigest(),'input_bytes_delivered':sum(s['bytes'] for s in supplied),'transport':'One named pipe per original native JSON file; full hash-verified bytes, unchanged parser and CLI, no substituted JSON fields. Each pipe closes at EOF.','scope':'Complete Bentham released-parser equivalence for six exported metrics. Historical Figure6 death-definition discrepancy remains.'}
(root/'audit.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report),flush=True)
