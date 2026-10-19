set -eu
root=/root/sugarscape/thaler-timing-continuation-001
input=/root/sugarscape/thaler-timing-continuation-input
mkdir "$root"
cd "$root"
exec > >(tee -a workflow.log) 2>&1
trap 'rc=$?; printf "%s\n" "$rc" > exit-code.txt; tar -czf /root/sugarscape/thaler-timing-continuation-evidence-001.partial.tar.gz --exclude="checkpoint-*" .; mv /root/sugarscape/thaler-timing-continuation-evidence-001.partial.tar.gz /root/sugarscape/thaler-timing-continuation-evidence-001.tar.gz; exit "$rc"' EXIT
cp "$input"/*.json "$input/run_timing.py" .
timeout 18000 bash -c 'until test -f /root/sugarscape/thaler-population-grid-evidence-001.tar.gz; do sleep 30; done'
cp /root/sugarscape/thaler-population-grid-001/exit-code.txt predecessor-exit-code.txt
cp /root/sugarscape/thaler-native-timing-002/results/manifest.json original-manifest.json
cat /sys/fs/cgroup/memory.events > memory-before.txt
timeout --signal=TERM --kill-after=30 15000 python3 run_timing.py /root/sugarscape/thaler-native-timing-002/source results --start-ordinal 41 --time-limit 14400
cat /sys/fs/cgroup/memory.events > memory-after.txt
