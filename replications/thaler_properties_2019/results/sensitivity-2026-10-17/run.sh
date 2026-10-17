set -eu
cd /root/sugarscape/thaler-properties-sensitivity-001
exec > >(tee run.log) 2>&1
for variant in index observation both; do
  cd "$variant"
  mkdir observer-build
  cd source
  stack ghc -- -O2 -isrc -odir ../observer-build -hidir ../observer-build ../Observe.hs -o ../observe
  cd ..
  ./observe mkParamsAnimationII_3 602352629 200 1 wealth
  ./observe mkParamsAnimationII_2 602352629 400 1 carrying
  ./observe mkParamsFigureIV_3 602352629 1000 1 trading
  printf '{"completed_trajectories":3}\n' > complete.json
  cd ..
done
printf '{"completed_variants":3}\n' > complete.json
