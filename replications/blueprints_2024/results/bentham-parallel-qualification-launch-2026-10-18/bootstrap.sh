#!/bin/bash
set -eu
cd /home/ubuntu/blueprints-bentham-qualification-001
exec > >(tee -a workflow.log) 2>&1
trap 'rc=$?; printf "%s\n" "$rc" > exit-code.txt; tar -czf /home/ubuntu/blueprints-bentham-qualification-evidence-001.partial.tar.gz --exclude=engine --exclude=venv .; mv /home/ubuntu/blueprints-bentham-qualification-evidence-001.partial.tar.gz /home/ubuntu/blueprints-bentham-qualification-evidence-001.tar.gz; exit "$rc"' EXIT
export DEBIAN_FRONTEND=noninteractive
timeout 600 bash -c 'apt-get update -qq && apt-get install -y -qq python3 python3-pip git curl ca-certificates'
python3 -m pip install uv==0.9.6
uv python install 3.11.14
uv venv --python 3.11.14 venv
uv pip install --python venv/bin/python pydantic==2.12.3
timeout 300 git clone --filter=blob:none --no-checkout https://github.com/digital-terraria-lab/sugarscape.git engine
git -C engine checkout --detach b9ca671ab7591c7b3606f2d76c33eda344d626d1
lscpu --json > lscpu.json
venv/bin/python -c 'import os,json; a=sorted(os.sched_getaffinity(0)); assert len(a)==64; print(json.dumps(a))' > affinity.json
timeout --signal=TERM --kill-after=30 3600 venv/bin/python run_batch.py engine blueprints-homogeneous.zip benthamHalfLookaheadBinary qualification --start 20 --stop 21
venv/bin/python - <<'CHECK'
import json
from pathlib import Path
p=json.loads(Path('protocol.json').read_text())
rows=[json.loads(x) for x in Path('qualification/completed.jsonl').read_text().splitlines()]
assert len(rows)==1 and rows[0]['seed']==p['qualification_seed']
assert rows[0]['result']['trajectory_sha256']==p['expected_trajectory_sha256']
assert rows[0]['result']['observations']==p['expected_observations']
Path('qualification-parity.json').write_text(json.dumps({'seed':p['qualification_seed'],'trajectory_sha256':p['expected_trajectory_sha256'],'exact_trajectory_match':True,'new_inputs_credited':0})+'\n')
CHECK
