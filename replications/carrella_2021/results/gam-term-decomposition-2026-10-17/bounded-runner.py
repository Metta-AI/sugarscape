import json,os,subprocess,time
from pathlib import Path
root=Path(__file__).parent
repo=Path('/Users/relh/Code/workspace/sugarscape-carrella/replications/carrella_2021')
reference=repo/'results/gam-fold2-runtime-diagnostic-2026-10-15/current/wealth.reproduction.rds'
started=time.monotonic()
for variant,directory in [('primary','gam-1250-2026-10-15'),('parser-control','gam-parser-control-complete-2026-10-17')]:
 command=['Rscript',str(repo/'diagnose_gam_terms.R'),str(repo/'results'/directory/'fold-2.rds'),str(reference),variant,str(root/variant)]
 (root/(variant+'-command.json')).write_text(json.dumps(command)+'\n')
 with (root/(variant+'.log')).open('x') as log:
  subprocess.run(command,stdout=log,stderr=subprocess.STDOUT,timeout=600,check=True,env=os.environ|{'R_LIBS_USER':'/Users/relh/Code/workspace/sugarscape-replication-tools/R-library','OPENBLAS_NUM_THREADS':'1','OMP_NUM_THREADS':'1'})
 assert sum(p.stat().st_size for p in root.rglob('*') if p.is_file())<100*1024**2
(root/'terminal.json').write_text(json.dumps({'exit_code':0,'elapsed_seconds':time.monotonic()-started,'per_variant_timeout':600})+'\n')
