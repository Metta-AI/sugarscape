#!/bin/bash
set -euo pipefail
cd /root/sugarscape/brearcliffe-existing-host-qualification-001
printf '%s\n' '184dffe53fbbde24d933715ec20722bb18cb1307970da60139f236793736cc36  trial-input.tar.gz' | sha256sum -c -
tar -xzf trial-input.tar.gz
export DEBIAN_FRONTEND=noninteractive
timeout --kill-after=30s 600 apt-get update
timeout --kill-after=30s 600 apt-get install -y openjdk-11-jre-headless fontconfig fonts-dejavu-core
java -version
python3 payload/qualify_host.py
tar -czf qualification-results.tar.gz payload/results payload/plan.json payload/cases.json payload/payload-sha256.json payload/gates actual-plan.json
sha256sum qualification-results.tar.gz
