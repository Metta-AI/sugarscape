set -eu
base=/root/sugarscape
mkdir "$base/richmond-full-native-001"
cd "$base/richmond-full-native-001"
exec > >(tee -a workflow.log) 2>&1
trap 'rc=$?; printf "%s\n" "$rc" > /root/sugarscape/richmond-full-native-001/exit-code.txt; tar -czf /root/sugarscape/richmond-full-native-evidence-001.tar.gz -C /root/sugarscape/richmond-full-native-001 .; exit "$rc"' EXIT
cp "$base/richmond-full-protocol.json" protocol.json
cp "$base/richmond-qualification-001/source-manifest.json" source-manifest.json
cp "$base/richmond-qualification-001/binary-sha256.txt" binary-sha256.txt
cp "$base/richmond-qualification-001/compiler.txt" compiler.txt
nvidia-smi -q > gpu.txt
git -C "$base/richmond-qualification-001/benchmark" diff --exit-code HEAD --
git -C "$base/richmond-qualification-001/engine" diff --exit-code HEAD --
python3 - <<'PY'
from pathlib import Path
import hashlib
p=Path('/root/sugarscape/richmond-qualification-001')
assert hashlib.sha256((p/'build/bin/Release/submodel-benchmark').read_bytes()).hexdigest()==(p/'binary-sha256.txt').read_text().split()[0]
PY
mkdir run
cd run
export FLAMEGPU2_INC_DIR="$base/richmond-qualification-001/engine/include"
set +e
timeout --signal=TERM --kill-after=30 21300 "$base/richmond-qualification-001/build/bin/Release/submodel-benchmark" > stdout.log 2> stderr.log
rc=$?
set -e
printf '%s\n' "$rc" > execution-exit-code.txt
cd ..
python3 - <<'PY'
from pathlib import Path
import json,hashlib,csv
root=Path('run');files={p.name:{'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in root.iterdir() if p.is_file()};counts={}
for p in root.glob('*.csv'):
 with p.open() as f:counts[p.name]=sum(1 for _ in csv.DictReader(f))
Path('qualification.json').write_text(json.dumps({'files':files,'csv_rows':counts,'execution_exit_code':int((root/'execution-exit-code.txt').read_text()),'scope':'Full unchanged benchmark attempt; completion determined by audited84-condition coverage, not process exit alone.'},indent=2)+'\n')
PY
exit "$rc"
