from pathlib import Path
import subprocess,json,gzip,hashlib,time
root=Path(__file__).parent
repo=Path('/Users/relh/Code/workspace/sugarscape-oremland/replications/oremland_2014')
ref=repo/'results/batch-evaluator-2026-10-18'
m=json.loads((ref/'manifest.json').read_text())
source=repo/'RunPolicyBatch.java'
(root/source.name).write_bytes(source.read_bytes())
cp=m['compile_command'][2].rsplit(':',1)[0]+':'+str(root)
compile_command=[m['compile_command'][0],'-cp',cp,'-d',str(root),str(root/source.name)]
subprocess.run(compile_command,check=True)
requests=gzip.decompress((ref/'requests.jsonl.gz').read_bytes());(root/'requests.jsonl').write_bytes(requests)
cmd=m['command'][:];cmd[cmd.index('-cp')+1]=cp;cmd[-2]=str(root/'requests.jsonl');cmd[-1]=str(root/'results.jsonl')
t=time.monotonic()
with (root/'run.log').open('x') as log: result=subprocess.run(cmd,stdout=log,stderr=subprocess.STDOUT)
(root/'exit.json').write_text(json.dumps({'exit_code':result.returncode,'seconds':time.monotonic()-t,'command':cmd},indent=2)+'\n')
assert result.returncode==0
old=[json.loads(s) for s in gzip.decompress((ref/'results.jsonl.gz').read_bytes()).splitlines()]
new=[json.loads(s) for s in (root/'results.jsonl').read_text().splitlines()]
assert len(old)==len(new)==400
for a,b in zip(old,new,strict=True):
 a.pop('elapsed_seconds');b.pop('elapsed_seconds');assert a==b
(root/'audit.json').write_text(json.dumps({'complete_native_runs':400,'exact_reference_results':400,'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'scope':'Full model parity only; extinction case pending.'},indent=2)+'\n')
print('400 complete native results match exactly',flush=True)
