set -u
cd /root/sugarscape/thaler-properties-001/source
.stack-work/dist/x86_64-linux-tinfo6/Cabal-2.2.0.1/build/sugarscape-model-test/sugarscape-model-test --quickcheck-replay=20261017 > /root/sugarscape/thaler-properties-model-suite-001/model-suite.log 2>&1
result=$?
printf '%s\n' "$result" > /root/sugarscape/thaler-properties-model-suite-001/exit-code.txt
exit "$result"
