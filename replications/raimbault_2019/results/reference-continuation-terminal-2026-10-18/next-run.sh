set -eu
root=/root/sugarscape/reference-continuation-002
input=/root/sugarscape/reference-continuation-input-002
mkdir "$root"
cd "$root"
exec > >(tee -a workflow.log) 2>&1
trap 'rc=$?; printf "{\"exit_code\":%s}\n" "$rc" > terminal.json; tar -czf /root/sugarscape/reference-continuation-evidence-002.tar.gz.pending .; mv /root/sugarscape/reference-continuation-evidence-002.tar.gz.pending /root/sugarscape/reference-continuation-evidence-002.tar.gz; exit "$rc"' EXIT
cp "$input/production-plan.json" "$input/run_reference_queue.py" .
timeout 10800 bash -c 'until test -f /root/sugarscape/generated-production-evidence-001.tar.gz; do sleep 30; done'
export DEBIAN_FRONTEND=noninteractive
timeout 600 bash -c 'apt-get update -qq && apt-get install -y -qq openjdk-11-jdk-headless python3 time'
java -version > java-version.txt 2>&1
python3 --version > python-version.txt
cat /sys/fs/cgroup/cpu.max > cpu-max.txt
timeout --signal=TERM --kill-after=30 7200 python3 run_reference_queue.py /root/sugarscape/proof-002 production-plan.json results
