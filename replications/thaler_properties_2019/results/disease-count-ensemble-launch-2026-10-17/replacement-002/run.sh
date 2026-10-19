set -eu
cd /root/sugarscape/thaler-properties-disease-count-ensembles-002
python3 run_disease_count.py protocol.json disease_count_corrected /root/sugarscape/thaler-properties-disease-count-ensembles-002/disease_count_corrected --start 1 --stop 100 > disease_count_corrected.stdout.log 2> disease_count_corrected.stderr.log
python3 run_disease_count.py protocol.json combined_corrected /root/sugarscape/thaler-properties-disease-count-ensembles-002/combined_corrected --start 1 --stop 100 > combined_corrected.stdout.log 2> combined_corrected.stderr.log
printf '{"completed_remaining_runs":198}\n' > complete.json
