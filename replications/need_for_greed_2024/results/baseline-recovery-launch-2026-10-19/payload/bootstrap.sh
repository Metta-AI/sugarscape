#!/bin/bash
set -eu
export DEBIAN_FRONTEND=noninteractive
apt-get update -qq
apt-get install -y -qq python3 python3-pip git curl ca-certificates procps
python3 -m pip install uv==0.9.6
uv python install 3.11.14
uv venv --python 3.11.14 venv
uv pip install --python venv/bin/python pydantic==2.12.3
curl -fsSL --max-time 120 https://raw.githubusercontent.com/digital-terraria-lab/datasets/0b50404c2529aa0ab08ce14c7f7abfe30fab837e/need-for-greed.zip -o need-for-greed.zip
printf '%s  %s\n' e41c89ed31811b2d100c0a54f9c0110f0572a980b599e2417b2653b934fbe440 need-for-greed.zip | sha256sum -c -
git -c 'alias.clone-lean=clone --filter=blob:none' clone-lean --no-checkout https://github.com/digital-terraria-lab/sugarscape.git engine
git -C engine checkout --detach b9ca671ab7591c7b3606f2d76c33eda344d626d1
set +e
venv/bin/python run_recovery.py
rc=$?
set -e
printf '%s\n' "$rc" > batch-exit-code.txt
timeout --kill-after=10 900 tar -czf terminal-evidence.tar.gz runs logs plan.json run_native.py source-sha256.json run_recovery.py bootstrap.sh batch-exit-code.txt
exit "$rc"
