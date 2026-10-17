from pathlib import Path
import subprocess,json,os,time
root=Path(__file__).resolve().parent;m=json.loads((root/'manifest.json').read_text());started=time.time()
with (root/'run.log').open('x') as log:result=subprocess.run(m['command'],cwd=m['cwd'],env=os.environ|m['env'],stdout=log,stderr=subprocess.STDOUT,timeout=m['timeout_seconds'])
(root/'exit.json').write_text(json.dumps({'exit_code':result.returncode,'elapsed_seconds':time.time()-started})+'\n')
