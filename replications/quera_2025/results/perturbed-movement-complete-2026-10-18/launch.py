import hashlib, json, os, shutil, signal, subprocess, time
from pathlib import Path
root=Path(__file__).resolve().parent
project=Path('/Users/relh/Code/workspace/sugarscape-diffabm-jmlr')
binary='/Users/relh/Code/workspace/sugarscape-replication-tools/julia-1.11.3-runtime-001/julia-1.11.3/bin/julia'
environment={**os.environ,'JULIA_DEPOT_PATH':'/Users/relh/Code/workspace/sugarscape-replication-tools/julia-depot-1.11.3-001','JULIA_NUM_THREADS':'1','JULIA_NUM_PRECOMPILE_TASKS':'1','JULIA_PKG_PRECOMPILE_AUTO':'0','OPENBLAS_NUM_THREADS':'1','PYTHON':'/Users/relh/Code/workspace/sugarscape-replications/.venv/bin/python'}
assert shutil.disk_usage(root).free>3*1024**3
command=[binary,'--startup-file=no','--project='+str(project),str(root/'run.jl'),str(project),str(root/'native'),'/Users/relh/Code/workspace/sugarscape-replication-evidence/quera-gradient-ensemble-001','perturbed','4','258']
run_started=time.time()
with (root/'run.log').open('x') as log:
    process=subprocess.Popen(command,cwd=project,env=environment,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
    (root/'process.json').write_text(json.dumps({'pid':process.pid,'command':command,'started':run_started,'timeout_seconds':7200,'runner_sha256':hashlib.sha256((root/'run.jl').read_bytes()).hexdigest()},indent=2)+'\n')
    reason='exited'
    try:
        while process.poll() is None:
            if time.time()-run_started>=7200:reason='timeout';break
            if shutil.disk_usage(root).free<2*1024**3:reason='disk_guard';break
            time.sleep(5)
    finally:
        if process.poll() is None:os.killpg(process.pid,signal.SIGKILL);process.wait()
        (root/'exit.json').write_text(json.dumps({'exit_code':process.returncode,'reason':reason,'elapsed_seconds':time.time()-run_started},indent=2)+'\n')
assert process.returncode==0
