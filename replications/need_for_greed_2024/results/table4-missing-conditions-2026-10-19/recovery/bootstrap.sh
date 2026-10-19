#!/bin/bash
set -eu
export DEBIAN_FRONTEND=noninteractive
/usr/bin/timeout --kill-after=15s 600s bash -c 'apt-get update -qq && apt-get install -y -qq git libffi8 libbz2-1.0 libsqlite3-0 libncursesw6 libexpat1 libtk8.6'
prior=/root/sugarscape/blueprints-selfishness037-batch-001
for name in engine cpython pypy blueprints-selfishness.zip; do
 test -e "$prior/$name"
 ln -s "$prior/$name" "$name"
done
cpython/bin/python -c 'import shutil; assert shutil.disk_usage(".").free >= 8*1024**3'
set +e
cpython/bin/python run_supplement_batch.py .
result=$?
set -e
printf '{"exit_code":%s}\n' "$result" > batch-terminal.json
/usr/bin/timeout --kill-after=15s 1200s tar -czf full-batch.tar.gz inputs runs audits logs protocol.json preparation.json source-sha256.json run_supplement.py audit_supplement.py run_supplement_batch.py bootstrap.sh versions.json completed.jsonl batch-terminal.json
exit "$result"
