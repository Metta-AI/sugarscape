set -eu
base=/root/sugarscape
root=$base/richmond-xorwow-control-001
mkdir "$root"
cd "$root"
exec > >(tee -a workflow.log) 2>&1
trap 'rc=$?; printf "%s\n" "$rc" > exit-code.txt; tar -czf /root/sugarscape/richmond-xorwow-control-evidence-001.tar.gz --exclude=build --exclude=source -C "$root" .; exit "$rc"' EXIT
timeout 600 bash -c 'apt-get update -qq && apt-get install -y -qq git cmake make g++ python3 ca-certificates'
old=$base/richmond-state-observer-001
engine=$base/richmond-qualification-001/engine
printf '%s  %s\n' 307bb4829ffef97b9eb004bdc59b58282aebd937c0bd4138581753bef711fba4 "$old/main.cu" | sha256sum -c -
test "$(git -C "$engine" rev-parse HEAD)" = 19136c18629af0a52ac4355ff705596b22bedac1
cp "$base/richmond-clang-input-control-002/clang.json" input.json
cp "$old/main.cu" main.cu
export FLAMEGPU2_INC_DIR="$engine/include"
mkdir philox
cd philox
timeout 300 "$old/build/bin/Release/submodel-benchmark" --in "$root/input.json" > stdout.log 2> stderr.log
printf '%s  %s\n' c713fc3663d5d87f8268964c3cc422cf498e38294477bde89229bb615a71adad state.csv | sha256sum -c -
cd ..
git -C "$base/richmond-qualification-001/benchmark" worktree add --detach "$root/source" 290702073492677f2fc9164419e9d5900d119e02
cp main.cu source/src/main.cu
timeout 300 cmake source -B build -DCMAKE_BUILD_TYPE=Release -DCMAKE_CUDA_ARCHITECTURES=90 -DFLAMEGPU_ROOT="$engine" -DFLAMEGPU_SEATBELTS=OFF -DFLAMEGPU_SHARE_USAGE_STATISTICS=OFF -DFLAMEGPU_CURAND_ENGINE=XORWOW > configure.log 2>&1
timeout 1200 cmake --build build -j 8 > build.log 2>&1
cp build/CMakeCache.txt cmake-cache.txt
find build -name flags.make -exec sh -c 'echo "$1"; cat "$1"' sh {} \; > compiler-flags.txt
python3 -c 'from pathlib import Path; t=Path("compiler-flags.txt").read_text(); assert "-DFLAMEGPU_CURAND_XORWOW" in t and "-DFLAMEGPU_CURAND_Philox4_32_10" not in t'
sha256sum build/bin/Release/submodel-benchmark > binary-sha256.txt
nvidia-smi -q > gpu.txt
mkdir xorwow
cd xorwow
timeout 300 ../build/bin/Release/submodel-benchmark --in "$root/input.json" > stdout.log 2> stderr.log
printf '0\n' > exit-code.txt
cd ..
