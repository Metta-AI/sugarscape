set -eu
cd /root/sugarscape/thaler-properties-observer-001
exec > >(tee build.log) 2>&1
mkdir observer-build
cd source
stack ghc -- -O2 -isrc -odir ../observer-build -hidir ../observer-build ../Observe.hs -o ../observe
cd ..
./observe mkParamsAnimationII_3 602352629 200 1 wealth
./observe mkParamsAnimationII_2 602352629 400 1 carrying
./observe mkParamsFigureIV_3 602352629 1000 1 trading
