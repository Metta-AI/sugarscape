#!/bin/bash
set -eu
cd /home/ubuntu/thaler-criterion-retry-control-001
printf 'SERVICE_RESULT=%s\nEXIT_CODE=%s\nEXIT_STATUS=%s\n' "$SERVICE_RESULT" "$EXIT_CODE" "$EXIT_STATUS" > service-result.txt
tar -czf /home/ubuntu/thaler-criterion-retry-control-evidence-001.partial.tar.gz .
mv /home/ubuntu/thaler-criterion-retry-control-evidence-001.partial.tar.gz /home/ubuntu/thaler-criterion-retry-control-evidence-001.tar.gz
