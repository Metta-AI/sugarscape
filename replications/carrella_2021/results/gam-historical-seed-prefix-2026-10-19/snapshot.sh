set -eu
cd /root/sugarscape/carrella-gam-historical-seeds-001
for seed in 01 02; do
  test -f seed-$seed/run/complete.txt
  grep -q '"exit_code":0' seed-$seed/terminal.json
done
mkdir /root/sugarscape/carrella-gam-historical-prefix-001
tar -czf /root/sugarscape/carrella-gam-historical-prefix-001/results.tar.gz inputs seed-01 seed-02 runtime.txt payload-check.txt SHA256SUMS run.sh
stat -c %s /root/sugarscape/carrella-gam-historical-prefix-001/results.tar.gz
sha256sum /root/sugarscape/carrella-gam-historical-prefix-001/results.tar.gz
