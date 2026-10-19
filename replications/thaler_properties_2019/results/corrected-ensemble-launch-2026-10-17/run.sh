set -eu
cd /root/sugarscape/thaler-properties-corrected-ensembles-001
exec > >(tee run.log) 2>&1
cd /root/sugarscape/thaler-properties-sensitivity-001/both/source
stack build --jobs 2
cd /root/sugarscape/thaler-properties-corrected-ensembles-001
python3 run_ensemble.py ../thaler-properties-sensitivity-001/both/source ensemble-protocol.json wealth wealth-ensemble --start 0 --stop 100 --seconds 7200 &
wealth_pid=$!
python3 run_ensemble.py ../thaler-properties-sensitivity-001/both/source ensemble-protocol.json carrying carrying-ensemble --start 0 --stop 100 --seconds 7200 &
carrying_pid=$!
python3 run_ensemble.py ../thaler-properties-sensitivity-001/both/source ensemble-protocol.json trading trading-ensemble --start 0 --stop 100 --seconds 7200 &
trading_pid=$!
wait "$wealth_pid"
wait "$carrying_pid"
wait "$trading_pid"
printf '{"completed_ensembles":3}\n' > complete.json
