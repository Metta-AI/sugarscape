set -euo pipefail
root=/root/sugarscape/brearcliffe-paper-host-qualification-001
mkdir -p "$root"
cd "$root"
export DEBIAN_FRONTEND=noninteractive
timeout --kill-after=30s 600 apt-get update
timeout --kill-after=30s 600 apt-get install -y python3 openjdk-11-jre-headless fontconfig fonts-dejavu-core
limit=$(( $(date +%s) + 1800 ))
while ! test -f input-ready; do test "$(date +%s)" -lt "$limit"; sleep 10; done
printf '%s
' '184dffe53fbbde24d933715ec20722bb18cb1307970da60139f236793736cc36  staged-input/trial-input.tar.gz' | sha256sum -c -
tar -xzf staged-input/trial-input.tar.gz
python3 payload/qualify_host.py
tar -czf qualification-results.tar.gz payload/results payload/plan.json payload/cases.json payload/payload-sha256.json payload/gates
stat -c %s qualification-results.tar.gz
sha256sum qualification-results.tar.gz
