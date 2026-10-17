set -eu
cd /root/sugarscape/thaler-culture-continuation-001
trap 'code=$?; printf "{\"exit_code\":%s}\n" "$code" > original-terminal.json; tar -czf /root/sugarscape/culture-original-evidence-001.tar.gz -C /root/sugarscape/thaler-culture-continuation-001 original original-terminal.json protocol.json run_culture.py; exit "$code"' EXIT
timeout --kill-after=30 7230 python3 -u /root/sugarscape/thaler-culture-continuation-001/run_culture.py /root/sugarscape/thaler-culture-continuation-001/protocol.json original /root/sugarscape/thaler-culture-continuation-001/original --start 33 --stop 100
