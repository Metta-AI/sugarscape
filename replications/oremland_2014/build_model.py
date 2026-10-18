"""Adapt NetLogo's constant-growback model to the printed 50x50 algorithm."""

import argparse
import hashlib
import json
from pathlib import Path

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("original", type=Path)
parser.add_argument("capacity", type=Path)
parser.add_argument("output", type=Path)
args = parser.parse_args()
original = args.original.read_text()
assert "NetLogo 5.3.1" in original
assert (
    hashlib.sha256(args.capacity.read_bytes()).hexdigest()
    == "cd9b4661c8813d3e268995676d5ba84394ee813986adb0d657dc9be4a1fab675"
)
code, interface = original.split("@#$#@#$#@", 1)
old_setup = """to setup
  clear-all
  create-turtles initial-population [ turtle-setup ]
  setup-patches
  reset-ticks
end"""
new_setup = """globals [tax-rate tax-phase clip-negative-payments total-tax debt-refund]

to setup
  setup-experiment 1 0.25 0 false
end

to setup-experiment [experiment-seed rate phase clipping?]
  clear-all
  resize-world 0 49 0 49
  set initial-population 200
  set tax-rate rate
  set tax-phase phase
  set clip-negative-payments clipping?
  random-seed experiment-seed
  create-turtles initial-population [ turtle-setup ]
  setup-patches
  reset-ticks
end"""
assert code.count(old_setup) == 1
code = code.replace(old_setup, new_setup)
assert code.count("set vision random-in-range 1 6") == 1
code = code.replace("set vision random-in-range 1 6", "set vision random-in-range 1 5")
start = code.index("to go\n")
stop = code.index("\nto turtle-move", start)
code = (
    code[:start]
    + """to go
  ask turtles [
    turtle-move
    turtle-eat
  ]
  ask patches [
    patch-growback
    patch-recolor
  ]
  if ticks mod 5 = tax-phase [
    ask turtles [
      let paid min (list sugar (ceiling (tax-rate * sugar)))
      set debt-refund debt-refund - min (list sugar 0)
      if clip-negative-payments [set paid max (list 0 paid)]
      set sugar sugar - paid
      set total-tax total-tax + paid
    ]
  ]
  ask turtles with [sugar <= 0] [die]
  tick
end

to-report survivor-state
  report (list
    (map [(list [who] of ? [xcor] of ? [ycor] of ? [sugar] of ? [metabolism] of ? [vision] of ?)] sort turtles)
    (map [(list [pxcor] of ? [pycor] of ? [psugar] of ? [max-psugar] of ?)] sort patches))
end
"""
    + code[stop:]
)
args.output.mkdir(parents=True, exist_ok=False)
(args.output / "oremland.nlogo").write_text(code + "@#$#@#$#@" + interface)
(args.output / "sugar-map.txt").write_bytes(args.capacity.read_bytes())
(args.output / "build.json").write_text(
    json.dumps(
        {
            "source_path": str(args.original),
            "source_sha256": hashlib.sha256(args.original.read_bytes()).hexdigest(),
            "capacity_sha256": hashlib.sha256(args.capacity.read_bytes()).hexdigest(),
            "adapted_model_sha256": hashlib.sha256(
                (args.output / "oremland.nlogo").read_bytes()
            ).hexdigest(),
            "builder_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            "scope": "Independent reconstruction of the published 50x50 algorithm using the retained NetLogo 5.3.1 constant-growback model. Not recovered author source. Uniform tax schedules are diagnostic controls, not the original 100 schedules. Phase 0 taxes after moves 1,6,...,46; phase 4 after moves 5,10,...,50. No scaled models or optimization implemented yet.",
        },
        indent=2,
    )
    + "\n"
)
