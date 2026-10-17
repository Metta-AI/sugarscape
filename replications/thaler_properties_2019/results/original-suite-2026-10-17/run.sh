set -eu
cd /root/sugarscape/thaler-properties-001
exec > >(tee build.log) 2>&1
trap 'rc=$?; printf "%s\n" "$rc" > exit-code.txt; tar -czf /root/sugarscape/thaler-properties-evidence-001.tar.gz --exclude=source .; exit "$rc"' EXIT
cd source
stack --version > ../versions.txt
stack build --test --no-run-tests --jobs 2
stack exec -- ghc --numeric-version >> ../versions.txt
stack test SugarScape:sugarscape-test --test-arguments="--quickcheck-replay=20261017" --jobs 2
