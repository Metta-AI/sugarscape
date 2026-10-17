set -eu
export DEBIAN_FRONTEND=noninteractive
apt-get update -qq
apt-get install -y -qq python3 python3-pip git curl ca-certificates
python3 -m pip install uv==0.9.6
mkdir source
cd source
uv python install 3.11.14
uv venv --python 3.11.14 venv
uv pip install --python venv/bin/python pydantic==2.12.3
curl -fsSL --max-time 120 https://raw.githubusercontent.com/Metta-AI/sugarscape/0eee2e6dfcd4c0b4f8b9acbf30c3d04eb2e4d7d4/replications/blueprints_2024/run_runtime.py -o run_runtime.py
curl -fsSL --max-time 120 https://raw.githubusercontent.com/Metta-AI/sugarscape/0eee2e6dfcd4c0b4f8b9acbf30c3d04eb2e4d7d4/replications/blueprints_2024/source-sha256.json -o source-sha256.json
curl -fsSL --max-time 120 https://raw.githubusercontent.com/digital-terraria-lab/datasets/0b50404c2529aa0ab08ce14c7f7abfe30fab837e/blueprints-runtimes.zip -o blueprints-runtimes.zip
printf '%s\n' 'df86e98f480c68abae4a3a647bcfe53bbce287c16850802e11c38eef8e6dd8d2  run_runtime.py' '1991484a4be6cbccfb57c29efa2c5aaa5f173882a4d795ae226122c3f8b964b8  source-sha256.json' '43b1967e9af9d7aac9785258706fd5abec6257235940b85aa811519c0e6ae98a  blueprints-runtimes.zip' | sha256sum -c -
git clone --filter=blob:none --no-checkout https://github.com/digital-terraria-lab/sugarscape.git engine
git -C engine checkout --detach b9ca671ab7591c7b3606f2d76c33eda344d626d1
cd ..
source/venv/bin/python run_recovery.py source cloud-plan.json runs
