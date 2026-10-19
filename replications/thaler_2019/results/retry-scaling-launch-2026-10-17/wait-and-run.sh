set -eu
timeout 39000 bash -c 'until test -f /root/sugarscape/thaler-native-timing-002/exit-code.txt; do sleep 30; done'
timeout --signal=TERM --kill-after=30 3300 bash /root/sugarscape/thaler-retry-scaling-input/execute.sh
