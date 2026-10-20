# Independent action replay

Three fixed-model scenarios complete 2,000 cycles each with seed 20261020:

| Scenario | Agent actions | Births | Deaths |
| --- | ---: | ---: | ---: |
| Infertility 85, birth cost 0 | 1,313,769 | 15,260 | 14,427 |
| Infertility 10, birth cost 40 | 1,321,432 | 2,219 | 1,402 |
| Infertility 10, birth cost 0 | 1,667,530 | 150,415 | 149,444 |

`audit_actions.py NEW_OUTPUT` compiles the pinned baseline and an instrumented copy, then runs both through their native command-line interface.
Both aggregate and individual observation outputs match byte-for-byte in all three scenarios.
The instrumentation records decisions without adding random draws; its exact generated source is retained.

Independent Python state replays all 4,302,731 actions.
Checks cover cardinal toroidal vision, nearest richest available destinations, occupancy, harvest, starvation, age increment, reproduction eligibility, adjacent birth locations, and delayed newborn activation.
Every cycle checks resource regrowth, population, wealth, mean age, and Gini against native output.
Activation order and random outcomes are inputs to replay; their historical identity and probability distributions are not independently established.

The negative control changes age increments to two in both compiled variants.
Their ordinary outputs still match, but independent replay rejects the first incorrect age transition.
Its result and traceback are retained; the simulator itself remains unchanged.

Compressed action tapes and baseline outputs have lossless readback checks in `published-readback.json`.
`audit.json` also hashes the original local executables, sources, and all uncompressed outputs; binaries are not published.

This validates implementation of the declared fixed-model rules for these runs.
It does not resolve undocumented historical conventions, test the evolutionary extension, explain the published age discrepancy, or complete the study.
