#!/bin/bash
set -eu
# The outer bound includes setup, qualification, simulations, audits and sealing.
exec /usr/bin/timeout --signal=TERM --kill-after=30s 42800s bash <<'BOUNDED_SWEEP'
set -eu
read -r sweep_started_boottime unused_idle_time < /proc/uptime
export SWEEP_STARTED_BOOTTIME="$sweep_started_boottime"
printf '{"started_boottime_seconds":%s,"outer_seconds":42800,"kill_grace_seconds":30}\n' "$sweep_started_boottime" > started.json
export DEBIAN_FRONTEND=noninteractive
apt-get update -qq
apt-get install -y -qq python3 python3-pip git curl ca-certificates time bzip2 libffi8 libbz2-1.0 libsqlite3-0 libncursesw6 libexpat1 libtk8.6
python3 -m pip install uv==0.9.6
uv python install 3.11.14
uv venv --python 3.11.14 cpython
uv pip install --python cpython/bin/python pydantic==2.12.3
git -c 'alias.clone-lean=clone --filter=blob:none' clone-lean --no-checkout https://github.com/digital-terraria-lab/sugarscape.git engine
git -C engine checkout --detach b9ca671ab7591c7b3606f2d76c33eda344d626d1
curl -fsSL --max-time 300 https://downloads.python.org/pypy/pypy3.11-v7.3.20-linux64.tar.bz2 -o pypy.tar.bz2
printf '%s  %s\n' 1410db3a7ae47603e2b7cbfd7ff6390b891b2e041c9eb4f1599f333677bccb3e pypy.tar.bz2 | sha256sum -c -
mkdir pypy
tar -xjf pypy.tar.bz2 -C pypy
curl -fsSL --max-time 300 https://raw.githubusercontent.com/digital-terraria-lab/datasets/0b50404c2529aa0ab08ce14c7f7abfe30fab837e/blueprints-selfishness.zip -o blueprints-selfishness.zip
printf '%s  %s\n' e2016f36a9728c23cee025d7a2e63cd2feffe4c36fbd62970e3a7792cb4d19e7 blueprints-selfishness.zip | sha256sum -c -
for runtime in cpython/bin/python pypy/pypy3.11-v7.3.20-linux64/bin/pypy3; do
 "$runtime" -c 'import bz2,sqlite3,ctypes,ssl; print(__import__("sys").version)'
done
cpython/bin/python -c 'import shutil; assert shutil.disk_usage(".").free >= 8*1024**3'
exec cpython/bin/python run_supplement_batch.py .
BOUNDED_SWEEP
