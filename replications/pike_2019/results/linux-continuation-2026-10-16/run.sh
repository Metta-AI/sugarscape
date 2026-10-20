#!/bin/sh
set -u
cd /root/sugarscape/pike-remaining-001
start=$(date +%s)
timeout --signal=TERM --kill-after=30s 21600 /root/sugarscape/pike-venv/bin/python run.py > launcher.log 2>&1
code=$?
printf '{"exit_code":%s,"started_unix":%s,"finished_unix":%s,"limit_seconds":21600}\n' "$code" "$start" "$(date +%s)" > terminal.json
tar -czf /root/sugarscape/pike-remaining-evidence-001.tar.gz -C /root/sugarscape/pike-remaining-001 .
exit "$code"
