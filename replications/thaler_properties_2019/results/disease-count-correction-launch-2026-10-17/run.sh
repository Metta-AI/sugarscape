set -eu
cd /root/sugarscape/thaler-properties-disease-count-001
exec > >(tee build.log) 2>&1
cd disease_count_corrected
mkdir observer-build first
cd source
stack build --test --no-run-tests --jobs 1
stack ghc -- -O2 -isrc -odir ../observer-build -hidir ../observer-build ../Observe.hs -o ../observe
cd ..
./observe mkParamsAnimationV_1 602352629 100 50 first/disease_clear > first/disease_clear.stdout.log 2> first/disease_clear.stderr.log
./observe mkParamsAnimationV_2 602352629 1000 50 first/disease_persist > first/disease_persist.stdout.log 2> first/disease_persist.stderr.log
cd ..
cd combined_corrected
mkdir observer-build first
cd source
stack build --test --no-run-tests --jobs 1
stack ghc -- -O2 -isrc -odir ../observer-build -hidir ../observer-build ../Observe.hs -o ../observe
cd ..
./observe mkParamsAnimationV_1 602352629 100 50 first/disease_clear > first/disease_clear.stdout.log 2> first/disease_clear.stderr.log
./observe mkParamsAnimationV_2 602352629 1000 50 first/disease_persist > first/disease_persist.stdout.log 2> first/disease_persist.stderr.log
cd ..
printf '{"completed_runs":4}\n' > complete.json
