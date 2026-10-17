from pathlib import Path
import json,subprocess,os,tarfile,hashlib,time
root=Path('/root/sugarscape/pike-common-cloud-zero-001');root.mkdir()
source=Path('/root/sugarscape/pike-portability-001')
runner=Path('/root/sugarscape/pike-common-cloud-ensemble-launch-001/run.py')
commands=[['/root/sugarscape/pike-venv/bin/python',str(runner),str(source/'engine'),str(source/'library'),variant,'0',str(root/variant)] for variant in ['common-one','common-multi']]
(root/'plan.json').write_text(json.dumps({'commands':commands,'scope':'Two missing native cloud seedzero conditions, same frozen runner and platform as198condition cloudgrid. Local seedzero pilots remain separate.'},indent=2)+'\n')
started=time.time()
for index,command in enumerate(commands):
 with (root/f'worker-{index}.log').open('x') as log:
  result=subprocess.run(command,stdout=log,stderr=subprocess.STDOUT,env=os.environ|{'PYTHONHASHSEED':'0','PYTHONDONTWRITEBYTECODE':'1'},timeout=240)
 (root/f'worker-{index}-exit.json').write_text(json.dumps({'exit_code':result.returncode})+'\n')
 assert result.returncode==0
(root/'exit.json').write_text(json.dumps({'exit_code':0,'elapsed_seconds':time.time()-started})+'\n')
archive=Path('/root/sugarscape/pike-common-cloud-zero-001.tar.gz')
with tarfile.open(archive,'w:gz') as t:t.add(root,arcname=root.name)
receipt={'bytes':archive.stat().st_size,'sha256':hashlib.sha256(archive.read_bytes()).hexdigest()}
Path('/root/sugarscape/pike-common-cloud-zero-001-export.json').write_text(json.dumps(receipt)+'\n');print(json.dumps(receipt))
