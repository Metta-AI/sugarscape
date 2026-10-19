#!/bin/bash
set -euo pipefail
mkdir /work/qualification
for variant in seq io tvar tarray; do
  cd /work/prepared/criterion/sugarscape-$variant
  stack build --jobs 1 > /work/qualification/$variant-build.log 2>&1
  stack exec -- ghc --numeric-version > /work/qualification/$variant-compiler.txt
  binary="$(stack path --local-install-root)/bin/sugarscape-$variant"
  sha256sum "$binary" > /work/qualification/$variant-binary.sha256
  runtime=()
  if [ "$variant" != seq ]; then runtime=(+RTS -N1 -RTS); fi
  for repetition in 1 2; do
    timeout 180 "$binary" 500 False "${runtime[@]}" > /work/qualification/$variant-normal-$repetition.csv 2> /work/qualification/$variant-normal-$repetition.stderr
  done
 done
printf '0\n' > /work/qualification/exit-code.txt
