# Buzing, Eiben and Schut (2005): source recovery and operational pilot

**Incomplete study. No paper-level replication verdict.**

Paper: [Emerging communication and cooperation in evolving agent societies](https://www.jasss.org/8/1/2.html).
It identifies JAWAS 1.2.3. Figures 3–5 compare communication protocols and cooperation thresholds;
Figure 4 overlays ten independent runs. Population, cooperation, and evolved talk/listen preferences are the targets.

## Recovered implementation

The [archived author project page](https://web.archive.org/web/20041011105638id_/http://www.cs.vu.nl:80/ci/eci/jawas/)
links JAWAS v2.2b. Its [archived download](https://web.archive.org/web/20061013011826id_/http://www.cs.vu.nl:80/%7Eschut/jawas/JAWAS.exe)
contains Java source and compiled dependencies. Despite the `.exe` suffix, it is a ZIP archive.
SHA-256: `f60a4fc96a419bbb72fe51990893f93cda5ff86f1b5668f9ffe887303ebed2e2`.

We compiled 78 unchanged model/data/util/experiment source files with OpenJDK 11.0.32.1.
The original command-line entry point hangs: `Experiment.launchNewScape()` is empty,
and `instantiateScape()` only constructs a model when GUI mode is enabled.
`Replay.java` invokes the existing initialization, execution, and result-writing lifecycle directly.
It changes no model rules. The 60-second completion bound is for this 100-cycle pilot only.

No redistribution license was located in the archive. Download the external reference separately;
this PR contains our adapter and generated numerical evidence, not the recovered source or binaries.
GitHub searches did not identify another relevant VUScape implementation; that is not proof none exists.

## Run the complete pilot workflow

Requires Python 3.11, Pydantic 2.12.3, and a JDK 11 installation. Use a new output directory.

```sh
curl -fL 'https://web.archive.org/web/20061013011826id_/http://www.cs.vu.nl:80/%7Eschut/jawas/JAWAS.exe' -o /absolute/JAWAS.exe
python replications/buzing_2005/run_pilot.py /absolute/JAWAS.exe /absolute/jdk11 /new/pilot
```

The runner verifies the archive hash, extracts it outside the repository, compiles the model,
copies its configuration, and sets GUI off, one run, 100 cycles, and nominal world seed zero.
It checks all seven scalar trajectories for 100 finite, consecutively indexed observations.
It also verifies the native completion message and records configuration/output hashes and runtime details.
The index starts at zero **after the first cycle**; the initial population is 1,000, not the first recorded population.

## Evidence and fidelity gaps

`results/pilot-2026-10-15` retains three completed native-model runs.
The first two used identical configuration and nominal seed zero, but ended at populations 471 and 438.
The complete acquisition/build/run workflow produced a third population of 421, with 700 validated scalar observations.
Different trajectories are expected from this release's incomplete seed control:
`Agent.java:26` constructs an unseeded `RandomMethods`, whose constructor uses `new Random()`.
`SugarAgent.java:174–215` consumes it for initial attributes; `Agent.java:271` consumes it for initial ages.
`Scape.java:294` seeds only the world's separate generator. Other random generators require further auditing.
We have not patched any generator or mistaken repeated nominal seeds for independent controlled replicates.

The recovered release also introduces two execution subcycles, explicitly described as new in version 2.0.
Version 1.2.3 equivalence has not been established. Its default experiment is not the paper's experiment:

| Setting | Archived default | Paper Table 2 / experiment |
| --- | --- | --- |
| Sugar richness | 1.4 | 1.0 |
| Initial sugar | 50–100 | 0–100 |
| Reproduction threshold | 0–100 | 0 |
| Talk/listen mutation | Disabled, sigma 0.01 | Enabled, sigma 0.1 |
| Message expiry | One iteration | COM1/COM2 removal rules |

These pilot outcomes therefore cannot support a negative replication.
Next: establish version and rule equivalence, map every experimental setting and measurement,
audit all active random-number paths, and predeclare the full figure comparisons before running them.
Any required source changes must be recorded as explicit patches and checked against the original model.

Earlier failed launches remain in the external evidence directory.
They include missing-config launches from incorrect working directories, the empty native CLI loop,
and an adapter compilation error before the nested `Experiment` subclass was introduced.
They are excluded from completed-run evidence, not erased or counted as scientific results.
