# Buzing, Eiben and Schut (2003): Evolving Agent Societies with VUScape

**Incomplete study. The 200-run reconstruction is fully audited; no paper-level replication verdict.**

[The author PDF](https://www.cs.vu.nl/~gusz/papers/ECAL2003-Buzing-Eiben-Schut.pdf) reports a distinct experiment from the 2005 paper.
DOI: `10.1007/978-3-540-39432-7_46`. Its hash and transcribed parameters are in [specification.json](specification.json).

This study uses 400 initial agents, sugar richness 0.5, growback 3, initial sugar 50, reproduction threshold 5, mutation sigma 0.01, and 500 cycles.
Communicating agents always listen; only talking evolves. Noncommunicating agents have both capabilities disabled.
The published plots overlay ten independent runs and report less population variation with communication.

## Native reconstruction

This branch depends on the 2005 source-recovery study. It reuses hash-verified native sources and configuration preparation, not that paper's simulation results.
The recovered archive is newer than the experiments. No exact historical release or publication seeds have been recovered.
Message removal is not pinned by the inspected 2003 text, so the runner requires an explicit policy:
`none`, `read`, `response`, or `expiry-one`. These are disclosed reconstruction alternatives, not recovered experimental settings.

The source retains balanced sugar seeds, alone-first harvesting, controlled random generators, and the declared sequential schedule from the source-recovery work.
By default, candidate fertility uses each parent's own bounds. Both parents must exceed the reproduction threshold at every birth.
Eligibility is checked again for each partner because earlier births can lower the initiating parent's sugar below five.
Newborn fertility-end age still follows the newer release's draw; historical inheritance and scheduling remain unresolved.
The native cooperation monitor and per-cycle harvest counts are retained separately.

No recovered author source or binaries are redistributed.

## Execute

Requires JDK11. The preparation step also requires Pydantic; the 2003 runner uses Python's standard library.
Use fresh output directories. Obtain the hash-pinned author archive following `replications/buzing_2005/README.md`.

```sh
python replications/buzing_2005/run_pilot.py ARCHIVE JAVA_HOME /new/preparation paper-com2 0 --threshold 1 --cycles 2000 --unpaced
python replications/buzing_2003/run_pilot.py /new/preparation /new/2003-response response 1 0
```

The preparation simulation is not counted as a 2003 run. Every study run recompiles verified native sources and records its own configuration, hashes, logs, and outputs.
The runner verifies 500 consecutive records in all seven scalar trajectories and fixed listening among living agents.
It also checks native completion, initial population 400, parental fertility, and sugar strictly above five at every observed birth.

## Evidence

[Five complete workflows](https://github.com/Metta-AI/sugarscape/blob/3a654712cb6f87b104c052b30d65d17fc4279c6c/replications/buzing_2003/results/pilot-2026-10-16/comparison.json) validate 17,500 scalar observations.
Two response-policy runs produce identical bytes in all ten native data files.
All four seed-zero, threshold-one policy conditions become extinct; their birth counts are 817 (response), 300 (none), 685 (read), and 625 (expiry-one).
These pilots do not reproduce the paper's survival findings and do not justify a negative replication.

A read-only initialization observer verifies 2,500 cells, 500 seeds, 1,250 sugar units, and 125 seeds of each maximum size 1–4.
All 18 Table 2 agent numeric settings were independently checked in actual configuration files.
The retained evidence includes native data, birth/harvest logs, exact configurations, source hashes, and all completed outcomes.

Remaining work: recover historical message semantics, audit scheduling and inheritance, and establish fidelity before interpreting the population and cooperation differences.

## Frozen grid

`run_ensemble.py REFERENCE_RUN NEW_OUTPUT` freezes the runner and shared adapter, then executes 200 bounded runs.
The grid crosses four declared policies, five thresholds, and ten seeds, each for 500 cycles.
The protocol discloses the observed seed-zero pilots. All outcomes and failures enter a completion ledger; a native failure stops the grid.
The three communicating policies bracket an unresolved setting. Choosing one after seeing agreement would not establish historical fidelity.
The first grid is complete and independently audited below; scientific interpretation remains limited by historical fidelity.

## Complete grid and initialization checks

[The complete audit](https://github.com/Metta-AI/sugarscape/blob/e952b1a3c3cb5749cea08bafd3a63e734535e855/replications/buzing_2003/results/complete-2026-10-16/audit.json) validates 200 runs, 700,000 scalar observations, and 182,401 births.
All populations become extinct between cycles 58 and 337, across all four declared policies and all five thresholds.
This fails to reproduce the reported survival pattern. It remains unresolved because historical source, reproduction, and scheduling fidelity are not established.
Zero late population variation after extinction must not be interpreted as beneficial stabilization.

`audit_ensemble.py ENSEMBLE complete NEW_OUTPUT` independently reads actual configurations, raw trajectories, fixed-listening values, and birth/harvest logs.
It reports temporal variation separately from variation across seeds. Incomplete grids and altered population files are rejected before creating output.
Four verified archives retain complete native data, configurations, manifests, and logs; original source and compiled classes are excluded.

`InitializationAudit.java` observes initialized native objects without advancing time or drawing randomness.
It verifies all 400 agents' actual sugar, metabolism, vision, communication values, age ranges, and reproduction thresholds.
It also checks all 500 seeds' size, composition, and actual growth rate of three.
Compile it against the run's classes and original library, then run `nl.vu.cs.sugarland.model.InitializationAudit` from a fresh directory containing the same configuration.
The retained observer used the communicating response-policy seed-zero pilot. Its first compilation referenced the wrong seed getter; that failure is preserved separately.
The corrected observer completes and confirms the configured initial state.

Next: isolate released versus specified reproduction behavior and scheduling, while preserving the entire failed-to-match reconstruction.

## Reproduction and subcycle diagnostics

The pilot accepts `--reproduction released` to retain recovered reproduction rules and `--subcycles 2` to select two native subcycles.
Defaults remain specified reproduction and one subcycle. The frozen grid and its auditor cover those defaults only.
These switches isolate candidate causes; neither setting establishes the unpublished historical schedule.

[Nine bounded diagnostics](https://github.com/Metta-AI/sugarscape/blob/3a654712cb6f87b104c052b30d65d17fc4279c6c/replications/buzing_2003/results/diagnostics-2026-10-16/comparison.json) retain 31,500 scalar observations and all native outputs.
All use seed zero and 500 cycles; they are diagnostics, not additional independent replication seeds.

| Reproduction | Subcycles | Policy | Threshold | Births | Outside own fertility range | At/below sugar threshold | Final population |
| --- | ---: | --- | ---: | ---: | ---: | ---: | ---: |
| Released | 1 | response | 1 | 825 | 115 | 22 | 0 |
| Specified | 1 | response | 1 | 817 | 0 | 0 | 0 |
| Released | 1 | none | 1 | 352 | 63 | 6 | 0 |
| Released | 1 | response | 0 | 866 | 105 | 27 | 0 |
| Released | 2 | response | 1 | 586 | 99 | 9 | 0 |
| Specified | 2 | response | 1 | 530 | 0 | 0 | 0 |
| Released | 2 | none | 1 | 362 | 78 | 8 | 0 |
| Released | 2 | response | 0 | 613 | 114 | 16 | 0 |

The first condition was repeated: all ten native data files match byte for byte.
The specified one-subcycle run also matches all ten files from the earlier pilot, despite the added fertility observer.
Restoring released reproduction or selecting two subcycles does not restore survival in these tested cases.
These checks do not establish a negative replication. Historical fidelity, inheritance, and resource dynamics remain under investigation.
Source inspection shows harvesting calls `cutAll`, followed by `takeSeeds`; the separate `cutAmount` method is not called on this path.

## Resource accounting at native recording boundaries

`audit_resources.py BASELINE_RUN NEW_OUTPUT` recompiles verified native sources with a passive seed observer.
It checks all cell plants and the redistribution bin at each recording boundary.
Every seed must be unique within that inventory, with 500 seeds total, 125 of each maximum size 1–4, and growth rate three.
Each plant's reported sugar must equal the sum of its seeds' current contents; each seed remains within its capacity.

[Four conditions plus a final-runner repeat](https://github.com/Metta-AI/sugarscape/blob/3a654712cb6f87b104c052b30d65d17fc4279c6c/replications/buzing_2003/results/resource-audit-2026-10-16/comparison.json) pass 2,500 cycle-boundary checks and all 50 native-file parity comparisons.
Conditions cover specified/released reproduction, one/two subcycles, and response/no communication, all at seed zero and threshold one.
These are diagnostic observations, not additional independent replication seeds.

Available sugar ranges from 809–1,250 across these runs. At most 169 seeds await redistribution at a recorded boundary.
The recovered schedule executes redistribution, then cell growth, then agent actions, then data recording.
Consequently, seeds harvested during a cycle wait for the next cycle's redistribution when `reseedPerIteration=true`.
This accounts for the observed bin contents; it does not establish that this newer schedule matches the historical experiment.
No seed loss or plant-accounting discrepancy appears at the checked boundaries. Intermediate-stage behavior and the survival mismatch remain unresolved.

## Archived raw outputs

[The immutable experiment archive](https://github.com/Metta-AI/sugarscape/tree/e952b1a3c3cb5749cea08bafd3a63e734535e855/replications/buzing_2003/results) retains raw runs and verbose diagnostics. They remain unchanged in existing local checkouts; summaries, source inputs, and analysis code stay tracked. Restore any required input with `git show e952b1a3c3cb5749cea08bafd3a63e734535e855:PATH > /absolute/output/path`, replacing `PATH` with its repository-relative path.

## Archived run records

Primary runners, analysis code, fixed study inputs, source provenance, and study findings remain tracked.
Dated run directories, checkpoint notes, copied runners, and generated source readbacks are preserved in [the experiment archive](https://github.com/Metta-AI/sugarscape/tree/0bb4c32d5a4c8fc14282a5acaf65e6f73b518532/replications/buzing_2003).
Regenerated evidence belongs in the ignored output directories.

Commands and provenance records may reference archived inputs or historical scripts. Restore those dependencies before running the corresponding analysis:

```sh
git restore --source=0bb4c32d5a4c8fc14282a5acaf65e6f73b518532 --worktree -- REPOSITORY_PATH
```

Replace `REPOSITORY_PATH` with the required archived file or directory. The restore leaves the index unchanged and the restored evidence ignored. The [original evidence archive](https://github.com/Metta-AI/sugarscape/tree/3a654712cb6f87b104c052b30d65d17fc4279c6c/replications/buzing_2003) retains raw outputs removed in previous cleanups.
