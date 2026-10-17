set -eu
timeout 21600 bash -c 'while [ ! -f /root/sugarscape/richmond-full-native-001/exit-code.txt ]; do sleep 15; done'
timeout --signal=TERM --kill-after=30 1800 bash /root/sugarscape/richmond-state-observer-input/run.sh
