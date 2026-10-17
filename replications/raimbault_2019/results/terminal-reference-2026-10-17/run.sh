set -eu
export DEBIAN_FRONTEND=noninteractive
root=/root/sugarscape/reference-continuation-001
mkdir "$root"
cd "$root"
exec > >(tee -a workflow.log) 2>&1
trap 'rc=$?; printf "{\"exit_code\":%s}\n" "$rc" > terminal.json; tar -czf /root/sugarscape/reference-continuation-evidence-001.tar.gz.pending -C "$root" .; mv /root/sugarscape/reference-continuation-evidence-001.tar.gz.pending /root/sugarscape/reference-continuation-evidence-001.tar.gz; exit "$rc"' EXIT
cp /root/sugarscape/reference-continuation-input/production-plan.json .
cp /root/sugarscape/reference-continuation-input/run_reference_queue.py .
timeout 600 bash -c 'apt-get update -qq && apt-get install -y -qq openjdk-11-jdk-headless python3'
java -version > java-version.txt 2>&1
python3 --version > python-version.txt
cat /sys/fs/cgroup/cpu.max > cpu-max.txt
timeout --signal=TERM --kill-after=30 16200 python3 run_reference_queue.py /root/sugarscape/proof-002 production-plan.json results
