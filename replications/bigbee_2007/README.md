# Bigbee, Cioffi-Revilla, and Luke (2007): Replication of Sugarscape Using MASON

Paper: [published chapter](https://doi.org/10.1007/978-4-431-71307-4_20).
The former author-hosted PDF URL now redirects to a department homepage; the local download was HTML, not a paper.
Status: author-source discovery, compilation, and deterministic pilot. **Not a completed replication.**

## Author source and historical limits

[BrentAuble/mason-sugarscape](https://github.com/BrentAuble/mason-sugarscape) mirrors the original Google Code project.
Pin: `2baa2e411f1be3e8da5e352de98468b42db3d75d`.
Its README identifies Tony Bigbee as the author and includes the thesis, conference draft, outcome configurations, and runtime dependencies.
The source and included dependencies retain their original license notices; the README identifies Academic Free License 3.0 for the main implementation.

This is a **2011 release**, not an authenticated 2007 experiment snapshot.
The earliest mirrored commit already updates version 1.1.2 for MASON 16.
The README explicitly warns that bug fixes after the thesis can change outcomes.
The paper discusses MASON 8. Historical source recovery or a documented version comparison is necessary before interpreting disagreements.

## Reproducible execution

The original command-line entry point selects the seed from wall-clock time.
`Replay.java` invokes the same public model constructor with an explicit seed and retains the original scheduling loop.
It disables chart display through the model's configuration API so that the headless model does not access GUI-only chart objects.
It does not change any agent or environment rule.

Compile all author simulation classes against the bundled libraries using OpenJDK 11.0.32.1.
From the pinned reference checkout, with an existing empty evidence directory:

```sh
mkdir /absolute/evidence/classes
rg --files sim/app/sugarscape -g '*.java' > /absolute/evidence/sources.txt
/path/to/jdk/bin/javac -cp 'lib/*' -d /absolute/evidence/classes @/absolute/evidence/sources.txt
/path/to/jdk/bin/java -Djava.awt.headless=true \
  -cp '/absolute/evidence/classes:lib/*:.' \
  /path/to/metta-ai-sugarscape/replications/bigbee_2007/Replay.java \
  conf/anim2-3.conf 0 1000 > /absolute/evidence/seed0.csv
```

The arguments are configuration path, seed, and final scheduled time.
The supplied configuration records statistics every ten timesteps and maintains a replacement population of 250.
The source model's loop advances while scheduled time is below the requested final time; this convention is preserved.

## Pilot evidence

[Retained evidence](results/pilot-2026-10-15) contains two byte-identical seed-zero runs, each reaching time 1,000.
All 101 observations have finite statistics, consecutive ten-step sampling times, and population 250.
The manifest hashes the source files, dependencies, configuration, and resulting trajectory.
The original failed headless attempt and its stack trace are retained: chart display was enabled in the supplied configuration.
Compilation and deterministic replay demonstrate execution, not agreement with any paper-level result.

## Required work

1. Recover the historical experiment code or audit differences between this release and the paper's implementation.
2. Extract and declare the complete Table 2 outcome targets, rule combinations, horizons, and quantitative or qualitative criteria.
3. Run the corresponding ensembles, including the paper's reported partial replications and discrepancies.
4. Validate equivalent behavior in the Metta-AI fork and preserve measurements sufficient to distinguish implementation errors from scientific disagreements.

A single replacement-population pilot does not establish reproduction of the paper's multiple rule-set outcomes.

## Provisional outcome inventory

[targets.json](targets.json) maps all 17 outcomes in Table 2 of the recovered April 2006 draft to existing configuration files.
Each configuration and the draft PDF are hashed. This draft is related evidence, not a verified substitute for the published 2007 table.
The targets cover movement, wealth, inequality, seasons, pollution, reproduction, culture, and trade.
Numerical thresholds, ensemble sizes, and temporal sampling remain to be declared before confirmatory execution.

## Complete draft-showcase execution audit

All seventeen draft configurations now run twice from a fresh compilation of the unchanged author release.
All 34 native processes exit successfully; paired logs are byte-identical across 28,466 observations.
[Execution audit](results/all-showcases-2026-10-15/audit.json) retains invalid measurements rather than treating successful execution as scientific validation.
Several reproduction cases emit nonfinite Gini statistics; the trade output contains an extra column absent from its header.
These runs use new seed zero and a common 1,000 scheduled-time horizon, not a recovered paper protocol.

A read-only `AuditReplay.java` inspects the live population counter, grid, and agent registry without changing native output.
Its `fig3-5` output is byte-identical to the original run, but [population accounting](results/all-showcases-2026-10-15/population-registry-audit.json) disagrees from reported time 13.
At that point the counter reports 413 agents, the grid contains 405 living agents, and the registry contains 400.
At the end those counts are 689, 683, and zero.

Source inspection identifies two reproduction defects in this 2011 release:
newborns are not inserted into the registry used by statistics, and `idFreeSpace` both reverses occupancy and checks a different direction from the returned cell.
The latter can overwrite an occupied cell. These defects must be corrected and validated before interpreting reproduction outcomes.
The original source and all failing measurements remain retained. No defect is attributed to the 2007 paper without historical evidence.

The alternative author URL `https://cs.gmu.edu/~sean/papers/Replication07.pdf` also redirects to a homepage as of this check.
Its downloaded body is HTML, despite a search index containing the old paper text; it is not used as a recovered published PDF.

## Corrected release validation

`reproduction-fixes.patch.gz` records three changes against the pinned 2011 release:
consistent empty-cell selection, newborn registration, and the missing trade column label.
The compressed patch preserves the author’s original CRLF source bytes.
Apply it to a separate checkout with `gzip -dc /path/to/reproduction-fixes.patch.gz | git apply`, preserving the original checkout.
The runner requires the exact declared source diff before compiling.

```sh
python replications/bigbee_2007/run_showcases.py /path/to/corrected-reference /path/to/jdk/bin corrected /absolute/evidence/corrected
python replications/bigbee_2007/audit_showcases.py /absolute/evidence/corrected /absolute/evidence/execution-audit
python replications/bigbee_2007/audit_populations.py /absolute/evidence/corrected /absolute/evidence/population-audit
```

[Corrected evidence](results/corrected-showcases-2026-10-15) retains all 34 native trajectories, compilation records, manifests, and seventeen population-observer trajectories.
All seventeen repeated pairs match byte-for-byte across 28,466 native observations.
Core statistics are finite and every output row matches its header width.
Average trade price remains undefined when no trades occur; no replacement value is introduced.

The observer reproduces each native output byte-for-byte.
Across 17,034 observed states, reported population, living grid occupants, registry size, and living registered agents agree exactly.
These checks establish the corrected population invariant under the tested scenarios, seed, and horizon.
They do not establish agreement with the 2007 paper or recover its historical implementation.
Original failing measurements remain alongside the corrected comparison.
