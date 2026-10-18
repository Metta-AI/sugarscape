set -eu
test ! -e /root/sugarscape/blueprints-runtime-memory-002
mkdir /root/sugarscape/blueprints-runtime-memory-002
printf '%s\n' '{"groups": [{"model": "rawSugarscape", "steps": 50000, "start": 66, "stop": 100}, {"model": "altruisticHalfLookaheadBinary", "steps": 50000, "start": 6, "stop": 100}], "seconds_per_group": 21600, "checkpoint_seconds": 1800}' > /root/sugarscape/blueprints-runtime-memory-002/cloud-plan.json
printf '%s\n' '952944cf4d7067ae643ef49ca2b5719a0d2984f6e720db8f1d328703c4e88c38  /root/sugarscape/blueprints-runtime-memory-001/run_recovery.py' | sha256sum -c -
exec /root/sugarscape/blueprints-runtime-memory-001/source/venv/bin/python /root/sugarscape/blueprints-runtime-memory-001/run_recovery.py /root/sugarscape/blueprints-runtime-memory-001/source /root/sugarscape/blueprints-runtime-memory-002/cloud-plan.json /root/sugarscape/blueprints-runtime-memory-002/runs
