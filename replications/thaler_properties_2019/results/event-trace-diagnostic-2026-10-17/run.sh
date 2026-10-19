set -eu
cd /root/sugarscape/thaler-properties-events-001
exec > >(tee build.log) 2>&1
mkdir observer-build reference traced
cd source
stack build --test --no-run-tests --jobs 1
stack ghc -- -O2 -isrc -odir ../observer-build -hidir ../observer-build ../Observe.hs -o ../observe
cd ..
/root/sugarscape/thaler-properties-observer-001/observe mkParamsAnimationII_3 602352629 200 1 reference/wealth > reference/wealth.stdout.log 2> reference/wealth.stderr.log
./observe mkParamsAnimationII_3 602352629 200 1 traced/wealth > traced/wealth.stdout.log 2> traced/wealth.stderr.log
/root/sugarscape/thaler-properties-observer-001/observe mkParamsAnimationII_2 602352629 400 1 reference/carrying > reference/carrying.stdout.log 2> reference/carrying.stderr.log
./observe mkParamsAnimationII_2 602352629 400 1 traced/carrying > traced/carrying.stdout.log 2> traced/carrying.stderr.log
/root/sugarscape/thaler-properties-observer-001/observe mkParamsFigureIV_3 602352629 1000 1 reference/trading > reference/trading.stdout.log 2> reference/trading.stderr.log
./observe mkParamsFigureIV_3 602352629 1000 1 traced/trading > traced/trading.stdout.log 2> traced/trading.stderr.log
/root/sugarscape/thaler-properties-observer-001/observe mkParamsAnimationIII_9 602352629 1000 1 reference/combat_culture > reference/combat_culture.stdout.log 2> reference/combat_culture.stderr.log
./observe mkParamsAnimationIII_9 602352629 1000 1 traced/combat_culture > traced/combat_culture.stdout.log 2> traced/combat_culture.stderr.log
/root/sugarscape/thaler-properties-observer-001/observe mkParamsAnimationIII_11 602352629 1000 1 reference/combat_rebirth > reference/combat_rebirth.stdout.log 2> reference/combat_rebirth.stderr.log
./observe mkParamsAnimationIII_11 602352629 1000 1 traced/combat_rebirth > traced/combat_rebirth.stdout.log 2> traced/combat_rebirth.stderr.log
printf '{"completed_cases":5}\n' > complete.json
