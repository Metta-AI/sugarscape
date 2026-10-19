set -eu
root=/root/sugarscape/generated-production-002
mkdir "$root"
cd "$root"
exec > >(tee -a workflow.log) 2>&1
trap 'rc=$?; printf "{\"exit_code\":%s}\n" "$rc" > terminal.json; tar -czf /root/sugarscape/generated-production-evidence-002.tar.gz.pending -C "$root" .; mv /root/sugarscape/generated-production-evidence-002.tar.gz.pending /root/sugarscape/generated-production-evidence-002.tar.gz; exit "$rc"' EXIT
cp /root/sugarscape/generated-production-input-002/{run.py,GeneratedReplay.java,expected-runtime.json,selection.json,selected.csv.gz} .
timeout 9000 bash -c 'while [ ! -f /root/sugarscape/reference-continuation-002/terminal.json ]; do sleep 30; done'
python3 - <<'PY'
import json
from pathlib import Path
p=Path('/root/sugarscape/reference-continuation-002/terminal.json')
assert json.loads(p.read_text())['exit_code'] in [0,124]
PY
export DEBIAN_FRONTEND=noninteractive
timeout 600 bash -c 'apt-get update -qq && apt-get install -y -qq openjdk-11-jdk-headless python3 time'
/usr/bin/time --version > gnu-time-bootstrap.txt
cat /sys/fs/cgroup/cpu.max > cpu-max.txt
cat /sys/fs/cgroup/cpuset.cpus.effective > cpuset.txt
timeout --signal=TERM --kill-after=30 10800 python3 run.py
