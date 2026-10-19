set -eu
export DEBIAN_FRONTEND=noninteractive
apt-get update -qq
apt-get install -y -qq git time
git --version
/usr/bin/time --version
/root/sugarscape/blueprints-runtime-memory-001/source/venv/bin/python -c 'import sys,pydantic; assert sys.version_info[:3] == (3,11,14); print(sys.version, pydantic.__version__)'
test "$(git -C /root/sugarscape/blueprints-runtime-memory-001/source/engine rev-parse HEAD)" = b9ca671ab7591c7b3606f2d76c33eda344d626d1
test -z "$(git -C /root/sugarscape/blueprints-runtime-memory-001/source/engine status --porcelain --untracked-files=no)"
df -h /root/sugarscape
test ! -e /root/sugarscape/blueprints-runtime-memory-004
mkdir /root/sugarscape/blueprints-runtime-memory-004
printf '%s\n' '{"groups": [{"model": "rawSugarscape", "steps": 50000, "start": 86, "stop": 100}, {"model": "altruisticHalfLookaheadBinary", "steps": 50000, "start": 22, "stop": 100}], "seconds_per_group": 21600, "checkpoint_seconds": 1800}' > /root/sugarscape/blueprints-runtime-memory-004/cloud-plan.json
printf '%s\n' '952944cf4d7067ae643ef49ca2b5719a0d2984f6e720db8f1d328703c4e88c38  /root/sugarscape/blueprints-runtime-memory-001/run_recovery.py' | sha256sum -c -
exec /root/sugarscape/blueprints-runtime-memory-001/source/venv/bin/python /root/sugarscape/blueprints-runtime-memory-001/run_recovery.py /root/sugarscape/blueprints-runtime-memory-001/source /root/sugarscape/blueprints-runtime-memory-004/cloud-plan.json /root/sugarscape/blueprints-runtime-memory-004/runs
