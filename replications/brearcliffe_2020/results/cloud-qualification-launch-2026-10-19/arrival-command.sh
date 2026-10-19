set -euo pipefail
mkdir -p /root/sugarscape/brearcliffe-cloud-qualification-001
cd /root/sugarscape/brearcliffe-cloud-qualification-001
for attempt in $(seq 1 60); do
  if test -f trial-input.tar.gz; then break; fi
  sleep 5
done
test -f trial-input.tar.gz
printf '%s  trial-input.tar.gz\n' 184dffe53fbbde24d933715ec20722bb18cb1307970da60139f236793736cc36 | sha256sum -c -
tar -xzf trial-input.tar.gz
bash bootstrap.sh
