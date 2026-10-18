#!/bin/bash
set -eu
export DEBIAN_FRONTEND=noninteractive
apt-get update -qq
apt-get install -y -qq python3 python3-pip git curl ca-certificates procps
python3 -m pip install uv==0.9.6
python3 -c 'import os; assert float(os.environ["GMN_CPU_LIMIT"]) >= 8; assert int(os.environ["GMN_MEMORY_LIMIT_BYTES"]) >= 32*1024**3'
curl -fsSL --max-time 120 https://raw.githubusercontent.com/digital-terraria-lab/datasets/0b50404c2529aa0ab08ce14c7f7abfe30fab837e/blueprints-homogeneous.zip -o blueprints-homogeneous.zip
printf "%s  %s\n" 319c38c77cdeb9f3bd618ce6c57e14e93c35e2be282c01332d42cff58327f525 blueprints-homogeneous.zip | sha256sum -c -
uv python install 3.11.14
uv venv --python 3.11.14 venv
uv pip install --python venv/bin/python pydantic==2.12.3
git -c 'alias.clone-lean=clone --filter=blob:none' clone-lean --no-checkout https://github.com/digital-terraria-lab/sugarscape.git engine
git -C engine checkout --detach b9ca671ab7591c7b3606f2d76c33eda344d626d1
venv/bin/python qualify.py
set +e
venv/bin/python run_selected.py engine blueprints-homogeneous.zip plan.json runs
rc=$?
set -e
printf '%s\n' "$rc" > exit-code.txt
venv/bin/python -c 'import json; from pathlib import Path; assert not json.loads(Path("runs/termination.json").read_text())["remaining_live_groups"]'
tar -czf terminal-evidence.partial.tar.gz runs qualification plan.json source-sha256.json run_selected.py run_batch.py run.py audit_batch.py bootstrap.log exit-code.txt
mv terminal-evidence.partial.tar.gz terminal-evidence.tar.gz
exit "$rc"
