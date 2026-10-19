#!/bin/bash
set -eu
cd /root/sugarscape/carrella-gam-historical-full-001
printf '%s  %s\n' '61a5c95f38738fa85432d898f27cb27dd39fe24056f460b87eb8db380fff2391' payload.tar.gz | sha256sum -c - > payload-check.txt
tar -xzf payload.tar.gz
Rscript --vanilla -e 'stopifnot(getRversion()=="4.0.5", packageVersion("mgcv")=="1.8.34", packageVersion("Matrix")=="1.3.2"); sessionInfo()' > runtime.txt
if timeout --kill-after=10 7200 env OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 Rscript --vanilla -e 'source("replay.R")' inputs run sensitivity > run.log 2>&1; then
  result_code=0
else
  result_code=$?
fi
printf '{"exit_code":%s}\n' "$result_code" > terminal.json
tar -czf results.tar.gz runtime.txt payload-check.txt terminal.json run.log replay.R inputs run
stat -c %s results.tar.gz
sha256sum results.tar.gz
exit "$result_code"
