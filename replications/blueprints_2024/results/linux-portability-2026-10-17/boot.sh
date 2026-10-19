set -eu
mkdir -p /root/sugarscape/blueprints-portability-001
cd /root/sugarscape/blueprints-portability-001
trap 'status=$?; printf "{\"exit_code\":%s}\n" "$status" > terminal.json; tar -czf /root/sugarscape/blueprints-portability-evidence-001.tar.gz --exclude=./engine/.git --exclude=./venv .; exit "$status"' EXIT
export DEBIAN_FRONTEND=noninteractive
apt-get update -qq
apt-get install -y -qq git curl ca-certificates python3 python3-pip libx11-6 libxft2 libxext6 libxrender1
python3 -m pip install uv==0.9.6
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
./venv/bin/python run_runtime.py engine blueprints-runtimes.zip rawSugarscape 500 pilot-raw --stop 1 --seconds 600
./venv/bin/python run_runtime.py engine blueprints-runtimes.zip altruisticHalfLookaheadBinary 500 pilot-altruistic --stop 1 --seconds 600
