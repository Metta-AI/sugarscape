#!/bin/bash
set -eu
cd /home/ubuntu/blueprints-bentham-parallel-001
test ! -e launch.pid
test -f plan.json
test -f stop-receipt.json
test -f local-completed.jsonl
# The previously recorded six-hour lease expires at 08:49:15 UTC.
# Reserve fifteen minutes for terminal sealing and evidence collection.
remaining=$((1792313355 - $(date +%s) - 900))
test "$remaining" -ge 3600
test "$remaining" -le 21600
printf '%s\n' "$remaining" > outer-seconds.txt
sudo -n nohup timeout --signal=TERM --kill-after=120 "$remaining" bash bootstrap.sh > launch.log 2>&1 < /dev/null &
echo $! > launch.pid
cat launch.pid
