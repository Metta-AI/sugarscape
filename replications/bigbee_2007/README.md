# Bigbee, Cioffi-Revilla, and Luke (2007): Replication of Sugarscape Using MASON

[The published Table 2 inventory](results/published-targets-2026-10-20) now maps all seventeen outcomes to frozen configuration hashes, paraphrased criteria, rule families, and author classifications. The earlier draft inventory remains intact. Missing per-row protocols and historical implementation qualifications remain; no new replication credit is assigned.

Paper: [published chapter](https://doi.org/10.1007/978-4-431-71307-4_20).
The [published eight-page PDF](https://people.cs.gmu.edu/~sean/papers/Replication07.pdf) was recovered from the author’s current faculty domain.
Status: historical releases and all seventeen showcase configurations executed; source and population-accounting discrepancies remain unresolved. **Not a completed replication.**

## Author source and historical limits

[BrentAuble/mason-sugarscape](https://github.com/BrentAuble/mason-sugarscape) mirrors the original Google Code project.
Pin: `2baa2e411f1be3e8da5e352de98468b42db3d75d`.
Its README identifies Tony Bigbee as the author and includes the thesis, conference draft, outcome configurations, and runtime dependencies.
The source and included dependencies retain their original license notices; the README identifies Academic Free License 3.0 for the main implementation.

The mirror is a **2011 release**. The separately recovered 1.1.2 archive is described as a 2007 release, but neither authenticates the paper’s experiment snapshot.
The earliest mirrored commit already updates version 1.1.2 for MASON 16.
The README explicitly warns that bug fixes after the thesis can change outcomes.
The published chapter discusses MASON 10; the earlier draft discusses MASON 8. Historical source recovery or a documented version comparison is necessary before interpreting disagreements.

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

[Retained evidence](https://github.com/Metta-AI/sugarscape/tree/1b4cd0477036d28b2f117a0d1b724424d40fa9b3/replications/bigbee_2007/results/pilot-2026-10-15) contains two byte-identical seed-zero runs, each reaching time 1,000.
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
[Execution audit](https://github.com/Metta-AI/sugarscape/blob/978716243eba3cda59175816142f5a28615ef95d/replications/bigbee_2007/results/all-showcases-2026-10-15/audit.json) retains invalid measurements rather than treating successful execution as scientific validation.
Several reproduction cases emit nonfinite Gini statistics; the trade output contains an extra column absent from its header.
These runs use new seed zero and a common 1,000 scheduled-time horizon, not a recovered paper protocol.

A read-only `AuditReplay.java` inspects the live population counter, grid, and agent registry without changing native output.
Its `fig3-5` output is byte-identical to the original run, but [population accounting](https://github.com/Metta-AI/sugarscape/blob/1b4cd0477036d28b2f117a0d1b724424d40fa9b3/replications/bigbee_2007/results/all-showcases-2026-10-15/population-registry-audit.json) disagrees from reported time 13.
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

[Corrected evidence](https://github.com/Metta-AI/sugarscape/tree/1b4cd0477036d28b2f117a0d1b724424d40fa9b3/replications/bigbee_2007/results/corrected-showcases-2026-10-15) retains all 34 native trajectories, compilation records, manifests, and seventeen population-observer trajectories.
All seventeen repeated pairs match byte-for-byte across 28,466 native observations.
Core statistics are finite and every output row matches its header width.
Average trade price remains undefined when no trades occur; no replacement value is introduced.

The observer reproduces each native output byte-for-byte.
Across 17,034 observed states, reported population, living grid occupants, registry size, and living registered agents agree exactly.
These checks establish the corrected population invariant under the tested scenarios, seed, and horizon.
They do not establish agreement with the 2007 paper or recover its historical implementation.
Original failing measurements remain alongside the corrected comparison.

## Recovered historical release and published chapter

[Source comparison](https://github.com/Metta-AI/sugarscape/blob/1b4cd0477036d28b2f117a0d1b724424d40fa9b3/replications/bigbee_2007/results/historical-source-2026-10-16/comparison.json) verifies the archive’s SHA-1 against the Google Code download catalog and records SHA-256 provenance.
The archive contains MASON 12 and Sugarscape 1.1.2; its README is dated November 25, 2007.
It still warns that post-thesis fixes can change outcomes, so it is not an authenticated experiment snapshot.

Agent.java and Reproduction.java match the 2011 mirror after line-ending normalization.
The population defects therefore occur in this older release as well; their presence in the published experiment remains unverified.
The retained diff records changes to scheduling API calls, resource loading, statistics output, and presentation code.
No original source was modified.

Visual inspection of published Table 2 (printed page 190, PDF page 8) confirms all seventeen outcome identifiers in the draft inventory.
The published classifications are four Exact, ten General, and three Partial.
These are the authors’ classifications, not results of this study.
The published chapter specifies MASON 10, correcting the prior README’s reliance on the draft’s MASON 8 description.
Historical scheduling differences and missing quantitative criteria still prevent a completed-study verdict.

Of seventeen outcome configurations, fourteen match after line-ending normalization.
One difference is a comment; `anim3-6` removes an explicit culture-output setting.
Crucially, `fig3-4` changes `reproduction_min` from 0 to 25.
The 2011 high-amplitude population pilot therefore does not use the recovered 2007 release’s fertility threshold.
Both configuration versions and their hashes remain preserved in the comparison evidence.

## Native historical-release audit

[Retained native evidence](https://github.com/Metta-AI/sugarscape/blob/1b4cd0477036d28b2f117a0d1b724424d40fa9b3/replications/bigbee_2007/results/historical-native-2026-10-16/audit.json) covers replacement (`anim2-3`) and reproduction (`fig3-4`, `fig3-5`).
Each uses seed zero and a 1,000 scheduled-time limit, with two native repeats and one read-only population observer.
All nine runs exit successfully; repeats and observer output match byte-for-byte within each configuration.

Compilation uses the archive’s MASON sources and bundled libraries with OpenJDK 11.
The unmodified build fails because modern Java introduces an ambiguous `Console` class name.
A separate source overlay qualifies `sim.display.Console`; original files remain untouched.
The patch, failed build, successful build, source/library hashes, and exact commands are retained.
No agent, environment, or scheduling rule is changed.

Replacement population accounting agrees in all 1,002 states.
Both reproduction configurations disagree in 989 of 1,002 states, beginning at time 13.
For `fig3-4`, the first reported/grid/registry counts are 408/405/400; final counts are 344/343/0.
For `fig3-5`, those counts are 407/402/399 initially and 872/862/0 finally.
The observer’s registered-living count also reaches zero despite living grid agents.
Native Gini debug lines and nonfinite outputs are preserved.

These measurements confirm population-accounting defects in the recovered release, using its original configurations.
They do not authenticate the historical experiment version or establish a negative replication of the chapter.

## MASON 10 framework comparison

The [toolkit authors' release catalog](https://people.cs.gmu.edu/~eclab/projects/mason/) still provides `mason10.zip`.
[Provenance and runtime comparison](https://github.com/Metta-AI/sugarscape/blob/1b4cd0477036d28b2f117a0d1b724424d40fa9b3/replications/bigbee_2007/results/mason10-runtime-2026-10-16/validated-runtime-comparison.json) pin the archive and loaded classes.
The archive contains no Sugarscape model, so recovering it does not authenticate the missing experiment snapshot.

The unchanged recovered 1.1.2 model runs with MASON 10 classes before its bundled framework on the classpath.
Class-loading logs confirm MASON 10 scheduling, random-number generator, and simulation classes.
Six ECJ parameter-loading classes still come from the model bundle; those fallback paths are explicitly retained.
Three seed-zero configurations run to scheduled time 1,000, each with an exact native-output and population-observer repeat.
All three native trajectories differ from the bundled MASON 12 runs, so framework version affects these outcomes.

Replacement population accounting agrees in all 1,002 states.
Both reproduction cases disagree in 989 states, starting at time 13.
For `fig3-4`, final reported/grid/registry populations are 323/321/0; for `fig3-5`, they are 673/667/0.
The earlier missing-newborn and occupied-cell defects therefore persist with the MASON 10 framework.
This rules out upgrading the framework alone as the explanation for those defects in the recovered model.
It does not establish that the paper used this model revision or justify a negative paper-level verdict.

## Historical download catalog recheck

[The complete Google Code download catalog](https://github.com/Metta-AI/sugarscape/tree/1b4cd0477036d28b2f117a0d1b724424d40fa9b3/replications/bigbee_2007/results/source-catalog-2026-10-18) lists only versions 1.1.2 and 1.1.3.
The 1.1.2 checksum matches the previously recovered and executed archive.
Its description dates the release to 2007; the catalog upload occurred in 2011.
Those dates are not interchangeable and neither proves which revision produced the paper’s results.
The bundled MASON 12 versus reported MASON 10 mismatch remains, as do the native accounting defects.
No earlier experiment snapshot was recovered from this catalog; other historical distribution sites remain possible.

## Archived author download page

[The December 2008 author-page snapshot](results/author-download-page-2026-10-18) pairs release 1.1.2 with MASON 12 and displays a November 25, 2007 release date. This corroborates the framework pairing before the 2011 mirror. Links to versions 1 and 1.1.1 were recovered, but their package bytes were not. The paper’s MASON 10 experiment snapshot remains unidentified.

## Archived source working copy

[The Google Code source snapshot audit](results/source-working-copy-2026-10-18) verifies all 870 ZIP entries and retains Subversion metadata plus core sources. Revision 24 has 2011 directory-change dates and identifies bundled MASON 16. Trunk and branch core files are identical; agent and reproduction rules match release 1.1.2 after newline normalization. This working-copy snapshot does not recover the historical paper revision or provide completion credit.

## Earlier package archive index

[Two bounded Wayback CDX prefix queries](https://github.com/Metta-AI/sugarscape/tree/1b4cd0477036d28b2f117a0d1b724424d40fa9b3/replications/bigbee_2007/results/earlier-package-index-search-2026-10-19) returned HTTP200 with no capture rows for the author’s former Mac download directory or Java.net project.
This extends the earlier exact-URL availability checks; it does not establish absence from other archives or URLs.
The unresolved artifact is the paper-era Sugarscape model source. MASON10 itself has already been recovered and tested above.

## Original bundled bytecode comparison

[All nine original-binary runs](results/bundled-binary-parity-2026-10-19) match the historical source rebuild byte-for-byte, including all 3,006 population-observer states. Class-loading logs verify original model, scheduler and random-generator bytecode; only the two replay wrappers are compiled. Both reproduction cases retain 989 accounting disagreements. This rules out modern recompilation as their cause in these checks, but does not authenticate the paper-era model or historical JVM.

## Archived raw outputs

[The immutable experiment archive](https://github.com/Metta-AI/sugarscape/tree/978716243eba3cda59175816142f5a28615ef95d/replications/bigbee_2007/results) retains raw runs and verbose diagnostics. They remain unchanged in existing local checkouts; summaries, source inputs, and analysis code stay tracked. Restore any required input with `git show 978716243eba3cda59175816142f5a28615ef95d:PATH > /absolute/output/path`, replacing `PATH` with its repository-relative path.

## Experiment evidence

Code, fixed study inputs, protocols, and written experiment summaries remain in this branch.
Generated run outputs, logs, checkpoints, and binary archives are excluded from the review diff.
The [immutable evidence archive](https://github.com/Metta-AI/sugarscape/tree/1b4cd0477036d28b2f117a0d1b724424d40fa9b3/replications/bigbee_2007) preserves the pre-cleanup files.
To restore an input, run `git show 1b4cd0477036d28b2f117a0d1b724424d40fa9b3:REPOSITORY_PATH > OUTPUT_PATH` from this repository.
Use the documented runners to regenerate outputs; local output directories remain untracked.
