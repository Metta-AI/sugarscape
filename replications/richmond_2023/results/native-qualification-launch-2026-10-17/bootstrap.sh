set -eu
export DEBIAN_FRONTEND=noninteractive
mkdir -p /root/sugarscape/richmond-qualification-001
cd /root/sugarscape/richmond-qualification-001
exec > >(tee -a bootstrap.log) 2>&1
trap 'rc=$?; printf "%s\n" "$rc" > exit-code.txt; tar -czf /root/sugarscape/richmond-qualification-evidence-001.tar.gz --exclude=benchmark --exclude=engine --exclude=build .; exit "$rc"' EXIT
printf '%s\n' 'Qualification only; unchanged complete benchmark with 600-second observation bound. Partial conditions do not complete the study.' > scope.txt
timeout 600 bash -c 'apt-get update -qq && apt-get install -y -qq git cmake make g++ python3 ca-certificates'
nvidia-smi -q > gpu.txt
nvcc --version > compiler.txt
g++ --version >> compiler.txt
cmake --version >> compiler.txt
printf '%s\n' "$GMN_CPU_LIMIT" "$GMN_MEMORY_LIMIT_BYTES" > resource-limits.txt
timeout 300 git clone --filter=blob:none --no-checkout https://github.com/FLAMEGPU/FLAMEGPU2-submodel-benchmark.git benchmark
git -C benchmark checkout --detach 290702073492677f2fc9164419e9d5900d119e02
timeout 300 git clone --filter=blob:none --no-checkout https://github.com/FLAMEGPU/FLAMEGPU2.git engine
git -C engine checkout --detach 19136c18629af0a52ac4355ff705596b22bedac1
python3 - <<'PY'
from pathlib import Path
import subprocess,json,hashlib
manifest={}
for root in [Path('benchmark'),Path('engine')]:
 files=subprocess.check_output(['git','-C',str(root),'ls-files','-z']).decode().split('\0')[:-1]
 manifest[str(root)]={'revision':subprocess.check_output(['git','-C',str(root),'rev-parse','HEAD'],text=True).strip(),'sha256':{n:hashlib.sha256((root/n).read_bytes()).hexdigest() for n in files}}
Path('source-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
PY
timeout 600 cmake benchmark -B build -DCMAKE_BUILD_TYPE=Release -DCMAKE_CUDA_ARCHITECTURES=90 -DFLAMEGPU_ROOT=/root/sugarscape/richmond-qualification-001/engine -DFLAMEGPU_SEATBELTS=OFF -DFLAMEGPU_SHARE_USAGE_STATISTICS=OFF -DBUILD_TESTS=OFF > configure.log 2>&1
jobs=$(python3 -c 'import os; print(min(8, int(float(os.environ["GMN_CPU_LIMIT"]))))')
timeout --signal=TERM --kill-after=30 3000 cmake --build build -j "$jobs" > build.log 2>&1
cp build/CMakeCache.txt CMakeCache.txt
sha256sum build/bin/Release/submodel-benchmark > binary-sha256.txt
mkdir run
cd run
export FLAMEGPU2_INC_DIR=/root/sugarscape/richmond-qualification-001/engine/include
set +e
timeout --signal=TERM --kill-after=30 600 ../build/bin/Release/submodel-benchmark > stdout.log 2> stderr.log
rc=$?
set -e
printf '%s\n' "$rc" > execution-exit-code.txt
cd ..
git -C benchmark diff --exit-code HEAD --
git -C engine diff --exit-code HEAD --
python3 - <<'PY'
from pathlib import Path
import json,hashlib,csv
root=Path('run')
files={p.name:{'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in root.iterdir() if p.is_file()}
counts={}
for p in root.glob('*.csv'):
 with p.open() as f:counts[p.name]=sum(1 for _ in csv.DictReader(f))
Path('qualification.json').write_text(json.dumps({'files':files,'csv_rows':counts,'execution_exit_code':int((root/'execution-exit-code.txt').read_text()),'scope':'Bounded native workflow qualification; not a completed ensemble or performance verdict.'},indent=2)+'\n')
PY
exit "$rc"
