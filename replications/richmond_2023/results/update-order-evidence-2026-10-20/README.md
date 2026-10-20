# Update order: published diagram and prose differ

The freshly downloaded paper matches the previously recorded SHA-256 exactly.
Visual inspection of Figure 6, printed page 11, confirms metabolism/growback precedes the movement submodel.
All nine audited native sources register those parent layers in that order.
Section 4.3 instead describes serial movement followed by harvest, metabolism, and death.
The release therefore follows the published diagram. Reversing the order would choose a different published interpretation, not unambiguously repair a code-only error.

The existing complete native worlds demonstrate why the ambiguity can matter at the first step.

| Maximum metabolism | Distance geometry | Observed first-step deaths | Deaths with an initially empty, resource-sufficient cardinal neighbor |
| --- | --- | ---: | ---: |
| 4 | direct or wrapped | 0 | 0 |
| 5 | direct | 22 | 3 |
| 5 | wrapped | 20 | 2 |

Both capacity caps give the same death and opportunity counts within each listed condition.
Every reported death identity is checked against the native first post-step state, not merely predicted from a population count.
The opportunities require a better-resource neighbor and strictly positive wealth after harvesting there and paying metabolism.
The report retains every candidate coordinate and the affected agent’s initial attributes.
Competition can prevent access, so these counts are not predicted rescues or movement-first simulation outcomes.

A layer swap alone would not implement the prose method: the metabolism function also initializes unresolved movement status.
Movement responses already harvest destination sugar, while transaction cleanup clears the source cell’s resource.
Those coupled operations require an explicit scheduling specification before any alternative execution can be called faithful.
Existing declared controls preserve the Figure 6 order. No parameters, source rules, or simulation outputs were changed for this audit.

Run `python replications/richmond_2023/audit_update_order.py NATIVE_EXTRACT_DIRECTORY NEW_REPORT.json` against the archive in the preceding initializer evidence.
The audit checks all nine source hashes, parent-layer order, complete 65,536-cell initial worlds, and observed first-step death identities.
`source-comparison.json` records paper provenance, page locations, visual readback hash, and the separate interpretations.
This resolves which published order the release follows. It does not resolve the paper’s inconsistency or establish a corrected whole-grid result.
