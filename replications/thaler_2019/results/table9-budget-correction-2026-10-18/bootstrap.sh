#!/bin/bash
set -eu
cd /home/ubuntu/sugarscape-table9-002
exec > >(tee -a bootstrap.log) 2>&1
trap 'rc=$?; printf "%s\n" "$rc" > exit-code.txt; tar -czf /home/ubuntu/sugarscape-table9-evidence-002.partial.tar.gz --exclude=source --exclude="checkpoint-*" .; mv /home/ubuntu/sugarscape-table9-evidence-002.partial.tar.gz /home/ubuntu/sugarscape-table9-evidence-002.tar.gz; exit "$rc"' EXIT
printf '%s  %s\n' 69166a06218a0177fc9da80e1e82b9e759843041fbb36cd515c2647e76538ab0 source-f5851488.tar.gz | sha256sum -c -
stack --version > versions.txt
uname -a >> versions.txt
lscpu >> versions.txt
mkdir source
tar -xzf source-f5851488.tar.gz -C source
python3 run_table9.py source results
