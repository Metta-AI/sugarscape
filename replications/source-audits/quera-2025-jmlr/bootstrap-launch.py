import hashlib, json, os, shutil, signal, subprocess, time
from pathlib import Path
root=Path(__file__).resolve().parent
project=Path('/Users/relh/Code/workspace/sugarscape-diffabm-jmlr')
binary='/Users/relh/Code/workspace/sugarscape-replication-tools/julia-1.11.3-runtime-001/julia-1.11.3/bin/julia'
depot='/Users/relh/Code/workspace/sugarscape-replication-tools/julia-depot-1.11.3-001'
command=[binary,'--startup-file=no','--project='+str(project),'-e','using Pkg; Pkg.instantiate(;allow_autoprecomp=false); println("INSTANTIATED"); using DiffABM; println("DIFFABM_LOADED")']
environment={**os.environ,'JULIA_DEPOT_PATH':depot,'JULIA_NUM_THREADS':'1','JULIA_NUM_PRECOMPILE_TASKS':'1','JULIA_PKG_PRECOMPILE_AUTO':'0','OPENBLAS_NUM_THREADS':'1','PYTHON':'/Users/relh/Code/workspace/sugarscape-replications/.venv/bin/python'}
assert shutil.disk_usage(root).free>12*1024**3
pins={name:hashlib.sha256((project/name).read_bytes()).hexdigest() for name in ['Project.toml','Manifest.toml']}
started=time.time()
with (root/'run.log').open('x') as log:
    process=subprocess.Popen(command,cwd=project,env=environment,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
    (root/'process.json').write_text(json.dumps({'pid':process.pid,'command':command,'started':started,'timeout_seconds':1800,'min_free_bytes':8*1024**3,'depot':depot,'source_hashes':pins},indent=2)+'\n')
    reason='exited'
    try:
        while process.poll() is None:
            if time.time()-started>=1800:
                reason='timeout';break
            if shutil.disk_usage(root).free<8*1024**3:
                reason='disk_guard';break
            time.sleep(5)
    finally:
        if process.poll() is None:
            os.killpg(process.pid,signal.SIGKILL);process.wait()
        after={name:hashlib.sha256((project/name).read_bytes()).hexdigest() for name in pins}
        (root/'exit.json').write_text(json.dumps({'exit_code':process.returncode,'reason':reason,'elapsed_seconds':time.time()-started,'project_and_manifest_unchanged':after==pins,'hashes_after':after},indent=2)+'\n')
