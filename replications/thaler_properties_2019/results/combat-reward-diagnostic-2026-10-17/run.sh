set -eu
cd /root/sugarscape/thaler-properties-combat-reward-001
exec > >(tee build.log) 2>&1
mkdir observer-build traced
cd source
stack build --test --no-run-tests --jobs 1
stack ghc -- -O2 -isrc -odir ../observer-build -hidir ../observer-build ../Observe.hs -o ../observe
cd ..
./observe mkParamsAnimationII_3 602352629 200 1 traced/wealth > traced/wealth.stdout.log 2> traced/wealth.stderr.log
./observe mkParamsAnimationII_2 602352629 400 1 traced/carrying > traced/carrying.stdout.log 2> traced/carrying.stderr.log
./observe mkParamsFigureIV_3 602352629 1000 1 traced/trading > traced/trading.stdout.log 2> traced/trading.stderr.log
./observe mkParamsAnimationIII_9 602352629 1000 1 traced/combat_culture > traced/combat_culture.stdout.log 2> traced/combat_culture.stderr.log
./observe mkParamsAnimationIII_11 602352629 1000 1 traced/combat_rebirth > traced/combat_rebirth.stdout.log 2> traced/combat_rebirth.stderr.log
printf '{"completed_cases":5}\n' > complete.json
