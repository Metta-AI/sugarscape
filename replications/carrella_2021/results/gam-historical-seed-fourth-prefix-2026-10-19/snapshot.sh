set -eu
cd /root/sugarscape/carrella-gam-historical-seeds-001
deadline=$(( $(date +%s) + 480 ))
while ! test -f seed-07/terminal.json || ! test -f seed-08/terminal.json; do
  test "$(date +%s)" -lt "$deadline"
  sleep 10
done
for seed in 07 08; do
  test -f seed-$seed/run/complete.txt
  grep -q '"exit_code":0' seed-$seed/terminal.json
done
mkdir /root/sugarscape/carrella-gam-historical-prefix-004
tar -czf /root/sugarscape/carrella-gam-historical-prefix-004/results.tar.gz inputs seed-07 seed-08 runtime.txt payload-check.txt SHA256SUMS run.sh
stat -c %s /root/sugarscape/carrella-gam-historical-prefix-004/results.tar.gz
sha256sum /root/sugarscape/carrella-gam-historical-prefix-004/results.tar.gz
