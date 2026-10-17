set -eu
root=/root/sugarscape/thaler-retry-scaling-001
mkdir "$root"
cd "$root"
exec > >(tee -a workflow.log) 2>&1
trap 'rc=$?; printf "%s\n" "$rc" > exit-code.txt; tar -czf /root/sugarscape/thaler-retry-scaling-evidence-001.partial.tar.gz --exclude=source .; mv /root/sugarscape/thaler-retry-scaling-evidence-001.partial.tar.gz /root/sugarscape/thaler-retry-scaling-evidence-001.tar.gz; exit "$rc"' EXIT
cp /root/sugarscape/thaler-retry-scaling-input/{protocol.json,run_retry_scaling.py} .
timeout --signal=TERM --kill-after=15 3200 python3 run_retry_scaling.py
