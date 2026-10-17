set -eu
export DEBIAN_FRONTEND=noninteractive
mkdir -p /root/sugarscape/thaler-culture-native-001
cd /root/sugarscape/thaler-culture-native-001
trap 'code=$?; printf "{\"exit_code\":%s}\n" "$code" > terminal.json; tar -czf /root/sugarscape/thaler-culture-parity-evidence-001.tar.gz -C /root/sugarscape thaler-culture-native-001; exit "$code"' EXIT
timeout --kill-after=30 600 sh -c 'apt-get update && apt-get install -y python3 libgmp10 ca-certificates curl'
curl --fail --location --retry 3 --connect-timeout 20 --max-time 180 https://raw.githubusercontent.com/Metta-AI/sugarscape/c21965cf440f7711a38dca572cc7d1e946378c70/replications/thaler_properties_2019/results/native-culture-parity-launch-2026-10-17/native-inputs.tar.gz -o native-inputs.tar.gz
printf "%s  %s\n" 76dd56eab9e600a1db33d22eb98cb83c19757547322bb05248e114106cc91524 native-inputs.tar.gz | sha256sum -c -
curl --fail --location --retry 3 --connect-timeout 20 --max-time 180 https://raw.githubusercontent.com/Metta-AI/sugarscape/c21965cf440f7711a38dca572cc7d1e946378c70/replications/thaler_properties_2019/results/native-culture-parity-launch-2026-10-17/parity-control-002.tar.gz -o parity-control-002.tar.gz
printf "%s  %s\n" ccae1f55e2bb55f389f9d55444b09d6420ee59ed67a9538ee1a10b2a3bc1e8c3 parity-control-002.tar.gz | sha256sum -c -
test ! -e /root/sugarscape/thaler-properties-observer-001
tar -xzf native-inputs.tar.gz -C /root/sugarscape
tar -xzf parity-control-002.tar.gz
uname -a > runtime.txt
python3 --version >> runtime.txt
ldd /root/sugarscape/thaler-properties-observer-001/observe >> runtime.txt
python3 -u parity.py
