# Combat cohort audit: incomplete prefix

The independent audit covers 24 matched culture pairs and one retained rebirth pair:
50 trajectories and 1,410,778 snapshot agent observations. Every-step population
accounting and all available snapshot IDs agree with the event logs. Initial agents,
cells, summaries, trading records, and resolved parameters match within each pair.
Original attacks retain the missing reward credit; corrected attacks credit it.
No ensemble confidence intervals or paper verdicts are reported.

`remaining-raw-data.tar.gz` contains the 46 newly audited runs, frozen worker ledgers,
and execution manifests. Restore CSV files with `gzip -dk` after extracting.
Four retained index-zero runs are already published in
`../event-trace-diagnostic-2026-10-17` and
`../combat-reward-diagnostic-2026-10-17`; the protocol pins their exact hashes.
Native source and binary verification requires the corresponding historical builds.
The `native_home` argument maps the recorded `/root/sugarscape` directory to its host path.

```
python audit_combat_ensemble.py protocol.json NATIVE_HOME EXTRACTED_RUNS NEW_AUDIT.json --allow-prefix
```

The frozen ledgers can contain additional unpaired completed runs. Their indices are
listed as unaudited; they are excluded from this archive and every comparison.
Omitting `--allow-prefix` requires all 100 pairs in both scenarios. The actual
unfinished cohorts fail this gate before writing an audit or ledger directory.
The full success path remains unverified until those native runs finish.

The 1,000-step horizon is an explicit diagnostic choice. This audit cannot establish
eventual single-agent convergence, spatial invasion, or a universal absence of invaders.
