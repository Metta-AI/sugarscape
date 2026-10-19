set -eu
cd /root/sugarscape/thaler-properties-spatial-001
exec > >(tee build.log) 2>&1
mkdir observer-build reference spatial
cd source
stack build --test --no-run-tests --jobs 1
stack ghc -- -O2 -isrc -odir ../observer-build -hidir ../observer-build ../Observe.hs -o ../observe
cd ..
/root/sugarscape/thaler-properties-observer-001/observe mkParamsAnimationII_6 602352629 1000 10 reference/migration > reference/migration.stdout.log 2> reference/migration.stderr.log
./observe mkParamsAnimationII_6 602352629 1000 10 spatial/migration > spatial/migration.stdout.log 2> spatial/migration.stderr.log
/root/sugarscape/thaler-properties-observer-001/observe mkParamsAnimationII_8 602352629 1000 10 reference/pollution > reference/pollution.stdout.log 2> reference/pollution.stderr.log
./observe mkParamsAnimationII_8 602352629 1000 10 spatial/pollution > spatial/pollution.stdout.log 2> spatial/pollution.stderr.log
./observe migrationVision15 602352629 1000 10 spatial/migration_vision15 > spatial/migration_vision15.stdout.log 2> spatial/migration_vision15.stderr.log
printf '{"completed_cases":3,"reference_cases":2}\n' > complete.json
