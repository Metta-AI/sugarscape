#!/bin/sh
set -u
cd /root/sugarscape/generated-sizing-001
start=$(date +%s)
timeout --signal=TERM --kill-after=30s 21600 python3 run.py > launcher.log 2>&1
code=$?
printf '{"exit_code":%s,"started_unix":%s,"finished_unix":%s,"limit_seconds":21600}\n' "$code" "$start" "$(date +%s)" > terminal.json
tar -czf /root/sugarscape/generated-sizing-evidence-001.tar.gz -C /root/sugarscape generated-sizing-001
curl --max-time 20 --noproxy '*' -fsS -X POST -H 'Metadata-Flavor: givemeanode' http://169.254.42.1/v1/stop
exit "$code"
