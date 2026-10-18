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
    hashlib.sha256(args.original.read_bytes()).hexdigest()
    == "761e8a921e9c876d12e5c1edcd5a00a3e1f8a11274c2a172c55c34a11103de2a"
)
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
new_setup = """globals [tax-schedule tax-phase clip-negative-payments total-tax debt-refund tax-events]

to setup
  setup-experiment 1 (n-values 200 [0.25]) 0 false
end

to setup-experiment [experiment-seed schedule phase clipping?]
  if length schedule != 200 [error "A tax policy must contain 200 entries"]
  if not empty? filter [not member? ? [0 0.25 0.5 0.75]] schedule [error "Invalid tax rate"]
  if not member? phase [0 4] [error "Invalid tax phase"]
  clear-all
  resize-world 0 49 0 49
  set initial-population 200
  set tax-schedule schedule
  set tax-events []
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
  set tax-events []
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
      let category 0
      if vision > 3 [set category category + 2]
      if metabolism > 2 [set category category + 1]
      let cycle floor (ticks / 5)
      let policy-index cycle * 20 + category * 5 + max-psugar
      let rate item policy-index tax-schedule
      let before sugar
      let paid min (list sugar (ceiling (rate * sugar)))
      set debt-refund debt-refund - min (list sugar 0)
      if clip-negative-payments [set paid max (list 0 paid)]
      set sugar sugar - paid
      set total-tax total-tax + paid
      set tax-events lput (list who vision metabolism max-psugar cycle policy-index rate before paid sugar) tax-events
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
            "scope": "Independent reconstruction of the published 50x50 algorithm using the retained NetLogo 5.3.1 constant-growback model. Not recovered author source. The policy contains 200 entries ordered by tax cycle, agent class LL/LH/HL/HH, and patch capacity 0..4. Generated diagnostic policies are not the original 100 schedules. Phase 0 taxes after moves 1,6,...,46; phase 4 after moves 5,10,...,50. No scaled models or optimization implemented yet.",
        },
        indent=2,
    )
    + "\n"
)
