#!/bin/bash
set -euo pipefail
cd /root/sugarscape/brearcliffe-cloud-qualification-001
export DEBIAN_FRONTEND=noninteractive
timeout --kill-after=30s 600 apt-get update
timeout --kill-after=30s 600 apt-get install -y python3 fontconfig fonts-dejavu-core
python3 payload/qualify_host.py
tar -czf qualification-results.tar.gz payload/results payload/plan.json payload/cases.json payload/payload-sha256.json payload/gates
