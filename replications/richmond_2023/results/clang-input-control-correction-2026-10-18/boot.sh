set -eu
root=/root/sugarscape/richmond-clang-input-control-002
mkdir "$root"
cd "$root"
exec > >(tee -a workflow.log) 2>&1
trap 'rc=$?; printf "%s\n" "$rc" > exit-code.txt; tar -czf /root/sugarscape/richmond-clang-input-control-evidence-002.tar.gz -C "$root" .; exit "$rc"' EXIT
for i in $(seq 1 180); do
  if test -f /root/sugarscape/richmond-clang-input-control-input-002.tar.gz; then break; fi
  sleep 1
done
printf '%s  %s\n' '0c70b7f534053eda4e3aeb6fedf4b637da1ef41e7c0c8ade33f33c819bd073f4' /root/sugarscape/richmond-clang-input-control-input-002.tar.gz | sha256sum -c -
tar -xzf /root/sugarscape/richmond-clang-input-control-input-002.tar.gz
old=/root/sugarscape/richmond-state-observer-001
printf '%s  %s\n' 307bb4829ffef97b9eb004bdc59b58282aebd937c0bd4138581753bef711fba4 "$old/main.cu" | sha256sum -c -
sha256sum "$old/build/bin/Release/submodel-benchmark" > binary-sha256.txt
cp "$old/main.cu" observer-main.cu
nvidia-smi -q > gpu.txt
export FLAMEGPU2_INC_DIR=/root/sugarscape/richmond-qualification-001/engine/include
for kind in gnu clang; do
  mkdir "$kind"
  cd "$kind"
  timeout --signal=TERM --kill-after=30 300 "$old/build/bin/Release/submodel-benchmark" --in "$root/$kind.json" > stdout.log 2> stderr.log
  printf '0\n' > exit-code.txt
  cd ..
done
