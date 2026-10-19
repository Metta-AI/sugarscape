set -eu
cd /root/sugarscape/carrella-gam-historical-seeds-001
deadline=$(( $(date +%s) + 480 ))
while ! test -f seed-05/terminal.json || ! test -f seed-06/terminal.json; do
  test "$(date +%s)" -lt "$deadline"
  sleep 10
done
for seed in 05 06; do
  test -f seed-$seed/run/complete.txt
  grep -q '"exit_code":0' seed-$seed/terminal.json
done
mkdir /root/sugarscape/carrella-gam-historical-prefix-003
tar -czf /root/sugarscape/carrella-gam-historical-prefix-003/results.tar.gz inputs seed-05 seed-06 runtime.txt payload-check.txt SHA256SUMS run.sh
stat -c %s /root/sugarscape/carrella-gam-historical-prefix-003/results.tar.gz
sha256sum /root/sugarscape/carrella-gam-historical-prefix-003/results.tar.gz
