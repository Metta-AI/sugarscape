set -eu
base=/root/sugarscape
while [ ! -f "$base/richmond-qualification-001/exit-code.txt" ]; do sleep 5; done
mkdir "$base/richmond-resolution-observer-001"
cd "$base/richmond-resolution-observer-001"
exec > >(tee -a workflow.log) 2>&1
trap 'rc=$?; printf "%s\n" "$rc" > /root/sugarscape/richmond-resolution-observer-001/exit-code.txt; tar -czf /root/sugarscape/richmond-resolution-observer-evidence-001.tar.gz -C /root/sugarscape/richmond-resolution-observer-001 --exclude=build --exclude=source .; exit "$rc"' EXIT
python3 - <<'PY'
from pathlib import Path
import json
p=Path('/root/sugarscape/richmond-qualification-001')
r=json.loads((p/'qualification.json').read_text())
assert r['execution_exit_code'] in [0,124]
PY
git -C "$base/richmond-qualification-001/benchmark" worktree add --detach "$base/richmond-resolution-observer-001/source" 290702073492677f2fc9164419e9d5900d119e02
cp "$base/richmond-observer-main.cu" source/src/main.cu
cp source/src/main.cu main.cu
git -C source diff HEAD -- > observer.patch
timeout 300 cmake source -B build -DCMAKE_BUILD_TYPE=Release -DCMAKE_CUDA_ARCHITECTURES=90 -DFLAMEGPU_ROOT="$base/richmond-qualification-001/engine" -DFLAMEGPU_SEATBELTS=OFF -DFLAMEGPU_SHARE_USAGE_STATISTICS=OFF > configure.log 2>&1
timeout 1000 cmake --build build -j 8 > build.log 2>&1
sha256sum build/bin/Release/submodel-benchmark > binary-sha256.txt
mkdir run
cd run
export FLAMEGPU2_INC_DIR="$base/richmond-qualification-001/engine/include"
timeout 120 ../build/bin/Release/submodel-benchmark > stdout.log 2> stderr.log
cd ..
