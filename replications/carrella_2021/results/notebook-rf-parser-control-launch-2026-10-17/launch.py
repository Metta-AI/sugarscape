import hashlib, json, os, shutil, signal, subprocess, time
from pathlib import Path
root=Path(__file__).resolve().parent
manifest=json.loads((root/'manifest.json').read_text())
assert not (root/'rf.rds').exists()
assert hashlib.sha256(Path(manifest['checkpoint']).read_bytes()).hexdigest()==manifest['checkpoint_sha256']
assert hashlib.sha256((root/'resume.R').read_bytes()).hexdigest()==manifest['runner_sha256']
source=Path('/Users/relh/Code/workspace/sugarscape-nofreelunch-reference')
for name,digest in manifest['source_sha256'].items():
    assert hashlib.sha256((source/name).read_bytes()).hexdigest()==digest
assert shutil.disk_usage(root).free > 2*1024**3
started=time.time()
with (root/'run.log').open('x') as log:
    process=subprocess.Popen(['/opt/homebrew/bin/Rscript',str(root/'resume.R')],stdout=log,stderr=subprocess.STDOUT,start_new_session=True,env={**os.environ,'R_LIBS_USER':'/Users/relh/Code/workspace/sugarscape-replication-tools/R-library','OMP_NUM_THREADS':'1','OPENBLAS_NUM_THREADS':'1'})
    (root/'process.json').write_text(json.dumps({'pid':process.pid,'started':started})+'\n')
    try:
        process.wait(timeout=manifest['timeout_seconds'])
    finally:
        if process.poll() is None:
            os.killpg(process.pid,signal.SIGKILL)
            process.wait()
        (root/'exit.json').write_text(json.dumps({'exit_code':process.returncode,'elapsed_seconds':time.time()-started})+'\n')
