set -eu
mkdir -p /home/dev/sugarscape/blueprints-runtime2-source-001
cd /home/dev/sugarscape/blueprints-runtime2-source-001
trap 'status=$?; printf "{\"exit_code\":%s}\n" "$status" > terminal.json; tar -czf /home/dev/sugarscape/blueprints-runtime2-setup-evidence-001.tar.gz --exclude=./engine/.git --exclude=./venv --exclude=./tool-venv .; exit "$status"' EXIT
export DEBIAN_FRONTEND=noninteractive
sudo apt-get update -qq
sudo apt-get install -y -qq git curl ca-certificates python3 python3-pip python3-venv libx11-6 libxft2 libxext6 libxrender1
python3 -m venv tool-venv
tool-venv/bin/pip install uv==0.9.6
export PATH="$(pwd)/tool-venv/bin:$PATH"
uv python install 3.11.14
uv venv --python 3.11.14 venv
uv pip install --python venv/bin/python pydantic==2.12.3
uv pip freeze --python venv/bin/python > requirements.txt
curl -fL https://raw.githubusercontent.com/Metta-AI/sugarscape/bf877f1/replications/blueprints_2024/run_runtime.py -o run_runtime.py
curl -fL https://raw.githubusercontent.com/Metta-AI/sugarscape/bf877f1/replications/blueprints_2024/source-sha256.json -o source-sha256.json
curl -fL https://raw.githubusercontent.com/digital-terraria-lab/datasets/0b50404c2529aa0ab08ce14c7f7abfe30fab837e/blueprints-runtimes.zip -o blueprints-runtimes.zip
printf '%s\n' 'df86e98f480c68abae4a3a647bcfe53bbce287c16850802e11c38eef8e6dd8d2  run_runtime.py' '1991484a4be6cbccfb57c29efa2c5aaa5f173882a4d795ae226122c3f8b964b8  source-sha256.json' '43b1967e9af9d7aac9785258706fd5abec6257235940b85aa811519c0e6ae98a  blueprints-runtimes.zip' | sha256sum -c -
git -c alias.clone-lean='clone --filter=blob:none' clone-lean --no-checkout https://github.com/digital-terraria-lab/sugarscape.git engine
git -C engine checkout --detach b9ca671ab7591c7b3606f2d76c33eda344d626d1
cat > /home/dev/sugarscape/run-blueprints-long5000-002.py <<'PY_RUNNER'
from pathlib import Path
import hashlib
import json
import subprocess
import sys
import tarfile
import time

source = Path('/home/dev/sugarscape/blueprints-runtime2-source-001')
root = Path('/home/dev/sugarscape/blueprints-long5000-002')
root.mkdir()
(root / 'run.py').write_bytes(Path(__file__).read_bytes())
assert hashlib.sha256((source / 'run_runtime.py').read_bytes()).hexdigest() == 'df86e98f480c68abae4a3a647bcfe53bbce287c16850802e11c38eef8e6dd8d2'
commands = []
for model in ['egoisticHalfLookaheadBinary', 'benthamHalfLookaheadBinary']:
    commands.append([str(source / 'venv/bin/python'), str(source / 'run_runtime.py'),
                     str(source / 'engine'), str(source / 'blueprints-runtimes.zip'),
                     model, '5000', str(root / model), '--seconds', '21600'])
plan = {'commands': commands, 'models': ['egoisticHalfLookaheadBinary', 'benthamHalfLookaheadBinary'],
        'steps': 5000, 'indices_per_model': [0, 100], 'conditions': 200,
        'parallel_workers': 2, 'per_worker_seconds': 21600, 'source': str(source),
        'scope': 'Unstarted originalruntime5000step groups. Distinct from500step localgroups; no claimedpaper500seed reconstruction.'}
(root / 'plan.json').write_text(json.dumps(plan, indent=2) + '\n')
started = time.time()
processes = []
for index, command in enumerate(commands):
    with (root / f'worker-{index}.log').open('x') as log:
        processes.append(subprocess.Popen(command, stdout=log, stderr=subprocess.STDOUT))
statuses = [process.wait() for process in processes]
(root / 'terminal.json').write_text(json.dumps({'exit_codes': statuses, 'elapsed_seconds': time.time()-started})+'\n')
archive = Path('/home/dev/sugarscape/blueprints-long5000-evidence-002.tar.gz')
with tarfile.open(archive, 'w:gz') as bundle:
    bundle.add(root, arcname='blueprints-long5000-002')
print(json.dumps({'archive': str(archive), 'sha256': hashlib.sha256(archive.read_bytes()).hexdigest(), 'exit_codes': statuses}), flush=True)
sys.exit(int(any(statuses)))
PY_RUNNER
timeout --kill-after=30s 21720s python3 /home/dev/sugarscape/run-blueprints-long5000-002.py
