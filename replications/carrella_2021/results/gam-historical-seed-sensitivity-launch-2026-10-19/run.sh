#!/bin/bash
set -eu
cd /root/sugarscape/carrella-gam-historical-seeds-001
sha256sum -c SHA256SUMS > payload-check.txt
Rscript --vanilla -e 'stopifnot(getRversion()=="4.0.5",packageVersion("mgcv")=="1.8.34",packageVersion("Matrix")=="1.3.2");sessionInfo()' > runtime.txt
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
run_one() {
  seed="$1"
  started=$(date +%s)
  if timeout --kill-after=10 4500 Rscript --vanilla -e "source('seed-$seed/replay.R')" inputs "seed-$seed/run" sensitivity > "seed-$seed/run.log" 2>&1; then
    code=0
  else
    code=$?
  fi
  ended=$(date +%s)
  printf '{"exit_code":%s,"started_unix":%s,"ended_unix":%s}\n' "$code" "$started" "$ended" > "seed-$seed/terminal.json"
  return "$code"
}
result=0
for pair in '01 02' '03 04' '05 06' '07 08' '09'; do
  pids=()
  for seed in $pair; do
    run_one "$seed" &
    pids+=("$!")
  done
  for pid in "${pids[@]}"; do
    if wait "$pid"; then :; else result=1; fi
  done
  if [ "$result" -ne 0 ]; then break; fi
done
printf '{"exit_code":%s}\n' "$result" > terminal.json
tar -czf results.tar.gz inputs seed-* runtime.txt payload-check.txt SHA256SUMS run.sh terminal.json
stat -c %s results.tar.gz
sha256sum results.tar.gz
exit "$result"
