#!/bin/bash
set -euo pipefail
cd /root/sugarscape/brearcliffe-existing-host-qualification-001
test ! -e payload/results
/root/sugarscape/blueprints-runtime-memory-001/source/venv/bin/python payload/qualify_host.py
tar -czf qualification-results.tar.gz payload/results payload/plan.json payload/cases.json payload/payload-sha256.json payload/gates actual-plan.json
sha256sum qualification-results.tar.gz
