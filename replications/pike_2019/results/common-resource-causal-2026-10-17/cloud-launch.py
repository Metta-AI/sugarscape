from pathlib import Path
import json,os,subprocess,time
root=Path('/root/sugarscape/pike-common-cloud-ensemble-launch-001')
source=Path('/root/sugarscape/pike-portability-001')
python='/root/sugarscape/pike-venv/bin/python'
output=Path('/root/sugarscape/pike-common-cloud-native-001')
command=[python,str(root/'run_common_resources.py'),str(source/'engine'),str(source/'library'),str(output)]
(root/'plan.json').write_text(json.dumps({'command':command,'scope':'Homogeneous x86 Linux native ensemble seeds1..99. Existing macOS60conditions remain a separate sensitivity series; do not pool. Prior cloudseed1controls are diagnostic duplicates, never double-count. Seedzero and lowerthresholds remain separate.'},indent=2)+'\n')
started=time.time()
with (root/'run.log').open('x') as log:
 result=subprocess.run(command,stdout=log,stderr=subprocess.STDOUT,env=os.environ|{'PYTHONHASHSEED':'0','PYTHONDONTWRITEBYTECODE':'1'},timeout=10800)
(root/'exit.json').write_text(json.dumps({'exit_code':result.returncode,'elapsed_seconds':time.time()-started})+'\n')
assert result.returncode==0
