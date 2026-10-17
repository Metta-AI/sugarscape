from pathlib import Path
import subprocess,json,os,time
root=Path('/root/sugarscape/pike-common-five-launch-001');controls=Path('/root/sugarscape/pike-common-threshold-controls-001')
assert json.loads((controls/'complete.json').read_text())=={'controls':2,'exact_file_comparisons':10}
source=Path('/root/sugarscape/pike-portability-001')
command=['/root/sugarscape/pike-venv/bin/python',str(root/'run_common_five.py'),str(source/'engine'),str(source/'library'),'/root/sugarscape/pike-common-five-001']
(root/'command.json').write_text(json.dumps(command)+'\n');started=time.time()
with (root/'run.log').open('x') as log:result=subprocess.run(command,stdout=log,stderr=subprocess.STDOUT,env=os.environ|{'PYTHONHASHSEED':'0','PYTHONDONTWRITEBYTECODE':'1'},timeout=10800)
(root/'exit.json').write_text(json.dumps({'exit_code':result.returncode,'elapsed_seconds':time.time()-started})+'\n');assert result.returncode==0
