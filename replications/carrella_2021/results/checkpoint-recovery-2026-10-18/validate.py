from pathlib import Path
import subprocess,os,json,time
root=Path(__file__).parent
inputs=root.parent/'carrella-independent-estimator-inputs-complete-001'
env=dict(os.environ,R_LIBS_USER='/Users/relh/Code/workspace/sugarscape-replication-tools/R-library')
for name,stop_after in [('interrupted',37),('resumed',0)]:
 command=['/opt/homebrew/bin/gtimeout','--signal=TERM','--kill-after=30','7200','/opt/homebrew/bin/Rscript',str(root/'run_checkpointed.R'),str(inputs),'sabc_1d','1250','0',str(root/name),str(root/'checkpoints'),str(stop_after)]
 start=time.monotonic()
 with (root/f'{name}.log').open('x') as log:
  result=subprocess.run(command,env=env,stdout=log,stderr=subprocess.STDOUT)
 (root/f'{name}-command.json').write_text(json.dumps({'command':command,'exit_code':result.returncode,'elapsed_seconds':time.monotonic()-start},indent=2)+'\n')
 if stop_after:
  assert result.returncode==1
  assert 'Requested interruption after durable observation checkpoint' in (root/f'{name}.log').read_text()
  assert len(list((root/'checkpoints').glob('fold-*/row-*.rds')))==37
 else:assert result.returncode==0
 print(name,result.returncode,flush=True)
comparison='''args <- commandArgs(TRUE)
original <- args[[1]]
resumed <- args[[2]]
for (fold in 1:5) {
  a <- readRDS(file.path(original, paste0("fold-", fold, ".rds")))
  b <- readRDS(file.path(resumed, paste0("fold-", fold, ".rds")))
  stopifnot(identical(a, b))
}
stopifnot(identical(readRDS(file.path(original,"complete.rds")),readRDS(file.path(resumed,"complete.rds"))))
stopifnot(identical(readLines(file.path(original,"metrics.csv")),readLines(file.path(resumed,"metrics.csv"))))
cat("All five full fold objects, predictions, intervals, RNG states and aggregate metrics are identical.\\n")
'''
(root/'compare.R').write_text(comparison)
p=subprocess.run(['/opt/homebrew/bin/Rscript',str(root/'compare.R'),str(root.parent/'carrella-independent-sabc1d-001/sabc_1d-1250'),str(root/'resumed')],env=env,capture_output=True,text=True)
(root/'comparison.json').write_text(json.dumps({'exit_code':p.returncode,'stdout':p.stdout,'stderr':p.stderr},indent=2)+'\n');assert p.returncode==0,p.stderr
print(p.stdout,flush=True)
