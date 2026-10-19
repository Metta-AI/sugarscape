set -eu
root=/root/sugarscape/thaler-population-grid-001
input=/root/sugarscape/thaler-population-grid-input
mkdir "$root"
cd "$root"
exec > >(tee -a workflow.log) 2>&1
trap 'rc=$?; printf "%s\n" "$rc" > exit-code.txt; tar -czf /root/sugarscape/thaler-population-grid-evidence-001.partial.tar.gz .; mv /root/sugarscape/thaler-population-grid-evidence-001.partial.tar.gz /root/sugarscape/thaler-population-grid-evidence-001.tar.gz; exit "$rc"' EXIT
cp "$input/protocol.json" "$input/run_population_grid.py" .
timeout 28800 bash -c 'until test -f /root/sugarscape/thaler-retry-scaling-evidence-001.tar.gz; do sleep 30; done'
cp /root/sugarscape/thaler-retry-scaling-001/exit-code.txt predecessor-exit-code.txt
timeout --signal=TERM --kill-after=30 10800 python3 run_population_grid.py "$input/prepared" protocol.json runs
