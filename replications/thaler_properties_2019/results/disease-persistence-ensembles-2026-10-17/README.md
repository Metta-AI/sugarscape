# Complete disease-persistence cohorts and configuration mismatch

All 100 seeds completed 1,000 steps under each source version. Independent audits
cover 200,200 summary observations and 894,627 snapshot agent observations.
Both published gzip archives reproduce their complete audit JSON exactly.

| Endpoint at step 1,000 | Historical source | Coordinate/observation corrected |
| --- | ---: | ---: |
| Infected majority | 81/100 | 81/100 |
| No infected agents | 16/100 | 16/100 |
| Extinct populations | 0/100 | 0/100 |

Both the code's `infected > ceil(population/2)` predicate and the prose's strict
majority predicate pass the same 81 cases within each version. The exact binomial
95% interval is [0.719302, 0.881557]. Two seeds exchange pass/fail status between
versions; identical totals do not mean identical trajectories. Failure cases and
first observed clearance times remain explicit in `comparison.json`.

## Why this is not a faithful 25-disease negative replication

The original `Scenario.hs` declares disease tuple fields as immune length, disease
count, maximum disease length, initial diseases per agent, and master list.
Animation V-2 supplies `(50,25,10,10,[])`, consistent with its comment and the
appendix's 25-disease description. But `Core/Init.hs:generateDiseaseMasterList`
uses the second field as maximum length and the third as count.

All 400 resolved V-1/V-2 configurations across both versions confirm the effect:
both scenarios generate ten entries. V-1 lengths span 1–10; V-2 lengths span 1–25.
V-2 has 9–10 distinct diseases, while V-1 has 8–10; generated entries are not
guaranteed distinct. Coordinate and observation corrections leave this mismatch
unchanged. These cohorts therefore measure the released implementation, not the
intended 25-disease configuration.

A separate bounded native validation corrects the generator's destructuring and
returned tuple order to match the declared contract. It preserves the historical
cohorts and requires byte-identical V-1 controls before expanding the experiment.
No conclusion from that pending correction is included here.

## Readback

Extract each `raw-data.tar.gz` into a common directory and restore CSV files with
`gzip -dk`. Each archive includes its execution manifest, runner, exact frozen
ledger, and all 100 disease-persistence outputs. The ledger also lists earlier
scenarios; their outputs were published separately and are not duplicated here.

```
python audit_observer_ensemble.py EXTRACTED/original protocol.json disease_persist NEW_AUDIT
python audit_observer_ensemble.py EXTRACTED/corrected protocol.json disease_persist OTHER_NEW_AUDIT
```

The configuration auditor additionally reads the earlier `disease_clear` outputs:

```
python audit_disease_configuration.py COMBINED_COHORT_ROOT protocol.json NEW_CONFIGURATION_AUDIT.json
```

This completes the historical 100-seed measurement, not the intended-configuration
replication or whole paper. The original model test suite leaves these properties
disabled; its default execution cannot resolve this discrepancy.
