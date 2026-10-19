set -eu
cd /root/sugarscape/thaler-properties-001/source
stack runghc -- /root/sugarscape/thaler-properties-native-seeds-001/GenerateSeeds.hs /root/sugarscape/thaler-properties-native-seeds-001/old-seeds.json /root/sugarscape/thaler-properties-native-seeds-001/native-seeds.json /root/sugarscape/thaler-properties-native-seeds-001/states.csv > /root/sugarscape/thaler-properties-native-seeds-001/generation.log 2>&1
