set -euo pipefail
root=/root/sugarscape/openabl-gpu-published-grid-001
engine=/root/sugarscape/openabl-gpu-qualification-001/engine
cd "$root"
tar -xzf input.tar.gz
seal() {
 cd "$root"
 tar -czf "$condition-evidence.tar.gz" "$condition" plan.json
 bytes=$(stat -c %s "$condition-evidence.tar.gz")
 hash=$(sha256sum "$condition-evidence.tar.gz" | cut -d ' ' -f1)
 printf 'SNAPSHOT {"archive":"%s/%s-evidence.tar.gz","bytes":%s,"sha256":"%s"}\n' "$root" "$condition" "$bytes" "$hash"
}
finish() {
 code=$?
 trap - EXIT
 printf '%s\n' "$code" > "$root/exit-code.txt"
 if [ "$code" -ne 0 ]; then seal; fi
 exit "$code"
}
condition=cells-500
trap finish EXIT
for size in 500 1000 2000 4000 8000 16000 32000 64000 128000 256000 512000 1024000; do
 condition=cells-$size
 cd "$root/$condition"
 available=$(df -B1 --output=avail . | tail -1)
 test "$available" -gt 50000000000
 make console-ext FLAMEGPU_DIR="$engine" SMS=90 "CONSOLE_INCLUDES=-I /usr/local/cuda/include -I $engine/include -I src/model -I src/dynamic -I src/visualisation" -j2 > build.log 2>&1
 bash build_runner.sh >> build.log 2>&1
 /usr/bin/time -v timeout --signal=TERM --kill-after=30 600 ./runner > run.log 2>&1
 test -s iterations/100.xml
 grep -q '<itno>100</itno>' iterations/100.xml
 seal
done
