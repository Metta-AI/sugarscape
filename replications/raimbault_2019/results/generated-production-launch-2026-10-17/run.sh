set -eu
root=/root/sugarscape/generated-production-001
mkdir "$root"
cd "$root"
exec > >(tee -a workflow.log) 2>&1
trap 'rc=$?; printf "{\"exit_code\":%s}\n" "$rc" > terminal.json; tar -czf /root/sugarscape/generated-production-evidence-001.tar.gz.pending -C "$root" .; mv /root/sugarscape/generated-production-evidence-001.tar.gz.pending /root/sugarscape/generated-production-evidence-001.tar.gz; exit "$rc"' EXIT
cp /root/sugarscape/generated-production-input/{run.py,GeneratedReplay.java,expected-runtime.json,selection.json,selected.csv.gz} .
timeout 18000 bash -c 'while [ ! -f /root/sugarscape/reference-continuation-001/terminal.json ]; do sleep 30; done'
python3 - <<'PY'
import json
from pathlib import Path
p=Path('/root/sugarscape/reference-continuation-001/terminal.json')
assert json.loads(p.read_text())['exit_code'] in [0,124]
PY
cat /sys/fs/cgroup/cpu.max > cpu-max.txt
cat /sys/fs/cgroup/cpuset.cpus.effective > cpuset.txt
timeout --signal=TERM --kill-after=30 10800 python3 run.py
