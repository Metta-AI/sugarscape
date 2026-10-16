# Buzing, Eiben and Schut (2003): Evolving Agent Societies with VUScape

**Incomplete study. Five native pilot runs completed; no paper-level replication verdict.**

[The author PDF](https://www.cs.vu.nl/~gusz/papers/ECAL2003-Buzing-Eiben-Schut.pdf) reports a distinct experiment from the 2005 paper.
DOI: `10.1007/978-3-540-39432-7_46`. Its hash and transcribed parameters are in [specification.json](specification.json).

This study uses400initial agents, sugar richness0.5, growback3, initial sugar50, reproduction threshold5, mutation sigma0.01, and500cycles.
Communicating agents always listen; only talking evolves. Noncommunicating agents have both capabilities disabled.
The published plots overlay ten independent runs and report less population variation with communication.

## Native reconstruction

This branch depends on the 2005 source-recovery study. It reuses hash-verified native sources and configuration preparation, not that paper's simulation results.
The recovered archive is newer than the experiments. No exact historical release or publication seeds have been recovered.
Message removal is not pinned by the inspected 2003 text, so the runner requires an explicit policy:
`none`, `read`, `response`, or `expiry-one`. These are disclosed reconstruction alternatives, not recovered experimental settings.

The source retains balanced sugar seeds, alone-first harvesting, controlled random generators, and the declared sequential schedule from the source-recovery work.
Candidate fertility uses each parent's own bounds. Both parents must exceed the reproduction threshold at every birth.
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
The runner verifies500consecutive records in all seven scalar trajectories and fixed listening among living agents.
It also checks native completion, initial population400, parental fertility, and sugar strictly above five at every observed birth.

## Evidence

[Five complete workflows](results/pilot-2026-10-16/comparison.json) validate17,500scalar observations.
Two response-policy runs produce identical bytes in all ten native data files.
All four seed-zero, threshold-one policy conditions become extinct; their birth counts are817(response),300(none),685(read), and625(expiry-one).
These pilots do not reproduce the paper's survival findings and do not justify a negative replication.

A read-only initialization observer verifies2,500cells,500seeds,1,250sugar units, and125seeds of each maximum size1–4.
All18Table2agent numeric settings were independently checked in actual configuration files.
The retained evidence includes native data, birth/harvest logs, exact configurations, source hashes, and all completed outcomes.

Remaining work: recover historical message semantics, audit scheduling and inheritance, run the full ten-seed grid, and compare population variation and cooperation curves.
