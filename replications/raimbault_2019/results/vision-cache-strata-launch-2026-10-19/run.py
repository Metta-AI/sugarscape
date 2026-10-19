import json,subprocess,time
from pathlib import Path
p=Path(__file__).resolve().parent
app=Path('/Users/relh/Code/workspace/sugarscape-replication-tools/netlogo-5.3.1-64/app')
protocol=json.loads((p/'protocol.json').read_text())
commands=[]
execution=p/'attempt-001';execution.mkdir()
for index,variant in enumerate(protocol['run_order']):
 d=execution/f'{index}-{variant}';d.mkdir()
 command=['/opt/homebrew/opt/openjdk@11/bin/java','-Djava.awt.headless=true','-Xmx768m','-cp',f'{app}/NetLogo.jar:{app}/*',str(p/'GiniReplay.java'),str(p/variant/'HEADLESS_Sugarscape.nlogo'),str(p/'selected.csv.gz'),'0','11',str(d/'results.csv')]
 commands.append(command)
 (d/'command.json').write_text(json.dumps(command,indent=2)+'\n')
 start=time.monotonic()
 with (d/'run.log').open('x') as log:
  result=subprocess.run(command,cwd=p/variant,stdout=log,stderr=subprocess.STDOUT,check=False,timeout=300)
 receipt={'exit_code':result.returncode,'elapsed_seconds':time.monotonic()-start}
 (d/'exit.json').write_text(json.dumps(receipt)+'\n');print(index,variant,receipt,flush=True)
 assert result.returncode==0
(execution/'complete.json').write_text(json.dumps({'runs':4,'inputs_per_run':11,'exit_code':0})+'\n')
