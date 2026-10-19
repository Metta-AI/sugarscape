#!/bin/bash
set -eu
cd /root/sugarscape/need-for-greed-baseline-recovery-002
prior=/root/sugarscape/need-for-greed-baseline-recovery-001
ln -s "$prior/engine" engine
ln -s "$prior/venv" venv
ln -s "$prior/need-for-greed.zip" need-for-greed.zip
set +e
venv/bin/python run_recovery.py
rc=$?
set -e
printf '%s\n' "$rc" > batch-exit-code.txt
timeout --kill-after=10 900 tar -czf terminal-evidence.tar.gz runs logs plan.json run_native.py source-sha256.json run_recovery.py bootstrap.sh failed-prefix.partial.gz batch-exit-code.txt terminal.json
exit "$rc"
