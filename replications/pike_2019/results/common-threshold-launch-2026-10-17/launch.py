from pathlib import Path
import subprocess,json,os,hashlib,time
root=Path('/root/sugarscape/pike-common-threshold-controls-001');source=Path('/root/sugarscape/pike-portability-001')
for variant in ['common-one','common-multi']:
 command=['/root/sugarscape/pike-venv/bin/python',str(root/'run_common_threshold.py'),str(source/'engine'),str(source/'library'),variant,'10','0',str(root/variant)]
 with (root/(variant+'.log')).open('x') as log:result=subprocess.run(command,stdout=log,stderr=subprocess.STDOUT,env=os.environ|{'PYTHONHASHSEED':'0','PYTHONDONTWRITEBYTECODE':'1'},timeout=240)
 (root/(variant+'-exit.json')).write_text(json.dumps({'exit_code':result.returncode,'command':command})+'\n');assert result.returncode==0
 expected=Path('/root/sugarscape/pike-common-cloud-zero-001')/variant
 actual=root/variant/'run'
 checks={name:hashlib.sha256((actual/name).read_bytes()).hexdigest()==hashlib.sha256((expected/name).read_bytes()).hexdigest() for name in ['initial-agents.json','observations.json','health.csv','population.csv','prices.json']}
 (root/(variant+'-parity.json')).write_text(json.dumps(checks,indent=2)+'\n');assert all(checks.values())
(root/'complete.json').write_text(json.dumps({'controls':2,'exact_file_comparisons':10})+'\n');print('Both1000stepcontrols passed10file comparisons')
