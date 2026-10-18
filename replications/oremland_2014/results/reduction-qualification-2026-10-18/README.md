# Native reduction qualification

All 24 declared parameter cases were built; byte-identical model/landscape pairs reduce these to 12 distinct executions.
Ninety-six full native runs completed across two seeds, both tax clocks, and both payment treatments.
The audit validates 4,896 state observations and 30,976 tax events.
The unchanged 50×50 case exactly reproduces the earlier detailed heterogeneous trajectory and event records for seeds 1 and 2.

The two map conventions are pixel-center nearest neighbor and aligned-endpoint nearest neighbor.
Population scales with area, preserving initial density 200/2500.
These are declared reconstruction choices; the paper does not specify the coordinates or population formula.

| Width | Initial agents | Radius by original vision 1, 2, 3, 4, 5 |
| --- | ---: | --- |
| 50 | 200 | 1, 2, 3, 4, 5 |
| 40 | 128 | 1, 1, 1, 3, 4 |
| 30 | 72 | 1, 1, 1, 2, 3 |
| 20, nearest rounding | 32 | 1, 1, 1, 2, 2 |
| 20, floor rounding | 32 | 1, 1, 1, 1, 2 |
| 10 | 8 | 1, 1, 1, 2, 2 |
| 5 | 2 | 1, 1, 1, 2, 2 |

The original sampled vision determines tax class; reducing a radius does not silently change the policy entry.
The full-size model stays byte-identical, including its original 1–5 vision distribution.
This distinguishes Appendix B's full-size description from section 4.24's reduced-model low-vision rule.
Nearest and floor rounding coincide except at width 20; some landscape conventions also produce identical maps.
All aliases and exact source indices remain recorded in `protocol.json` and `audit.json`.

The audit reads initial agents and patches from the actual NetLogo workspace.
It verifies population, occupancy, complete map orientation/capacity, vision-point counts, retained class, policy indices, every payment, cumulative revenue, and paired survivor hashes.
The driver checks toroidal distance across both boundaries at every model size.
All archived files pass byte-for-byte readback; the archive retains executed sources, model files, runtime manifests, outputs, and terminal statuses.

This qualifies the declared implementations. It does not recover the author's reduction choices, establish the policy-ranking claim, or complete the paper.
