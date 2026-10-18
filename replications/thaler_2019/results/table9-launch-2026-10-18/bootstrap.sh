#!/bin/bash
set -eu
cd /home/ubuntu/sugarscape-table9-001
exec > >(tee -a bootstrap.log) 2>&1
trap 'rc=$?; printf "%s\n" "$rc" > exit-code.txt; tar -czf /home/ubuntu/sugarscape-table9-evidence-001.tar.gz --exclude=source --exclude="checkpoint-*" --exclude=payload.tar.gz .; exit "$rc"' EXIT
export DEBIAN_FRONTEND=noninteractive
printf '%s  %s\n' 69166a06218a0177fc9da80e1e82b9e759843041fbb36cd515c2647e76538ab0 source-f5851488.tar.gz | sha256sum -c -
timeout 600 bash -c 'apt-get update -qq && apt-get install -y -qq haskell-stack git curl ca-certificates gcc make libgmp-dev libtinfo5 freeglut3-dev python3'
mkdir -p /root/.stack
cp stack-global-config.yaml /root/.stack/config.yaml
stack --version > versions.txt
uname -a >> versions.txt
lscpu >> versions.txt
mkdir source
tar -xzf source-f5851488.tar.gz -C source
timeout --signal=TERM --kill-after=30 10200 python3 run_table9.py source results
