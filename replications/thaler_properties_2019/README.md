# Thaler and Siebers (2019): property testing

Incomplete study. Original property/ensemble workflows were exercised, while disabled tests, source/prose discrepancies, and remaining appendix scenarios prevent a completed paper verdict.

Sources: [publication 1](https://www.researchgate.net/publication/333198243_SHOW_ME_YOUR_PROPERTIES_THE_POTENTIAL_OF_PROPERTY-BASED_TESTING_IN_AGENT-BASED_SIMULATION).

## Retained workflow

Retains the frozen three-scenario ensemble, upstream source manifest, and complete-ensemble auditor. Combat, disease, culture, spice, observer, and plotting investigations are archived.

Use the pinned prerequisites from the archived study. Uppercase arguments denote supplied paths or identifiers; output paths must be new.

```sh
python replications/thaler_properties_2019/run_ensemble.py AUTHOR_ENGINE replications/thaler_properties_2019/ensemble-protocol.json wealth NEW_RUN --start 0 --stop 100 --seconds 21600
python replications/thaler_properties_2019/audit_ensemble.py NEW_RUN --output NEW_AUDIT
```

## Historical study and evidence

The [pinned study record](https://github.com/Metta-AI/sugarscape/tree/c5dbc9ad49e7c2f2a7c3eca5e9ccfd7370cdc078/replications/thaler_properties_2019) retains full campaigns, removed scripts, reference outputs, source revisions, and dependency environments. It also links earlier raw-data archives.

Findings above describe that recorded study. The retained workflow covers the entrypoints listed here. Export historical files outside this checkout; generated diagnostics belong in temporary or explicitly chosen output directories.
