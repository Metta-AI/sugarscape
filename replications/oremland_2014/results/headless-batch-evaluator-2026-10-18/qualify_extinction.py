from pathlib import Path
import json,gzip,subprocess
root=Path(__file__).parent
old=root.parent/'oremland-rankings-001'
name='5-pixel_centers-nearest'
completed=sum(1 for _ in (old/'execution'/f'{name}-shard-0.results.jsonl').open())
with gzip.open(old/name/'requests-0.jsonl.gz','rb') as f:
 for i,line in enumerate(f):
  if i==completed: break
request=json.loads(line)
(root/'extinction-request.jsonl').write_bytes(line)
base=json.loads((root/'exit.json').read_text())['command']
base[-3]=str(old/name/'oremland.nlogo');base[-2]=str(root/'extinction-request.jsonl');base[3]='120'
records={}
for kind in ['original','headless']:
 cmd=base[:];cmd[-1]=str(root/(kind+'-extinction.jsonl'))
 if kind=='original': cmd[cmd.index('-cp')+1]=cmd[cmd.index('-cp')+1].rsplit(':',1)[0]+':'+str(old/'execution')
 with (root/(kind+'-extinction.log')).open('x') as log: r=subprocess.run(cmd,stdout=log,stderr=subprocess.STDOUT)
 records[kind]={'command':cmd,'exit_code':r.returncode}
 if kind=='original':
  assert r.returncode!=0
  assert "Can't find the maximum of a list with no numbers: []" in (root/(kind+'-extinction.log')).read_text()
 else:
  assert r.returncode==0
  result=json.loads((root/(kind+'-extinction.jsonl')).read_text())
  assert result['population']==0 and result['steps']==50
  assert result['id']==request['id'] and result['seed']==request['seed']
  records[kind]['result']=result
(root/'extinction-audit.json').write_text(json.dumps({'original_completed_prefix':completed,'request':request,'executions':records,'scope':'Exact failed input reproduces original plot crash; plot-free adapter completes all 50 steps with zero survivors. Full-model 400-case parity recorded separately.'},indent=2)+'\n')
print('Original extinction crash reproduced; headless 50-step completion verified.')
