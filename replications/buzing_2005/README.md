# Buzing, Eiben and Schut (2005): source recovery and reconstruction

**Incomplete study. The 150-run reconstruction is audited; historical fidelity and paper-level replication remain unresolved.**

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
python replications/buzing_2005/run_pilot.py /absolute/JAWAS.exe /absolute/jdk11 /new/pilot original 0
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

## Controlled random-generator variant

The source audit finds seven unseeded `new Random()` constructions in four compiled files.
They cover `RandomMethods` (including agent initialization), two torus operations, three sugar-agent communication/reproduction operations, and correspondent cache selection.
The `controlled` runner variant replaces exactly those seven constructor expressions in the extracted experimental copy.
`ReplicationRandom.java` derives a separate generator seed from a seeded master stream in construction order.
The world's existing explicit seed is preserved. This is a declared experimental variant, not recovered historical source.

Run `run_pilot.py ARCHIVE JDK NEW_OUTPUT controlled SEED`.
The original variant remains available explicitly as `original SEED` for comparison.
Manifests record every compiled source hash, exact replacement counts, seed, runtime, configuration, and output hashes.
No source from the archive is redistributed.

[Three completed workflows](results/seed-control-2026-10-15/comparison.json) validate 2,100 scalar observations.
Two independent seed-zero processes produce identical bytes in all ten output files and final population 450.
Seed one produces a different trajectory and final population 307.
This establishes repeatability for the tested defaults, seed pair, runtime, and 100-cycle horizon only.
It does not validate unused communication branches or the paper's version 1.2.3.

Earlier attempts completed native simulations but failed while serializing our manifest because a local replacement-count variable was reused.
That runner defect was fixed; fresh full workflows then completed successfully. Failure tracebacks remain retained separately.
Paper-specific communication rules, subcycle equivalence, and full experimental settings remain unresolved.

## Protocol and landscape audit

[configuration-map.json](configuration-map.json) records provisional parameter and communication mappings, with unresolved semantics kept explicit.
`LandscapeAudit.java` initializes the native model and reads its cells without advancing time or drawing random numbers.
The [seed-zero observation](results/landscape-table2-2026-10-15) changes only sugar richness from the release default to 1.0.
The 2,500 cells contain exactly 2,500 sugar units but 1,015 seeds; 161 cells contain multiple seeds.
There are 102 cells above four sugar units, with a maximum of eleven.
Thus setting the seed-size limit to four does not bound this release's cell piles at four.

Source inspection finds another explicit version change in `SugarAgent.harvest`: version 2.0 shares whenever multiple agents occupy a food-bearing cell.
The source comment describes the older behavior as consuming alone whenever possible.
`TorusScape.executeRules` also has distinct one-subcycle and multiple-subcycle paths.
The paper's model therefore cannot be recovered merely by applying its scalar parameter table to this newer release.
These observations identify implementation-alignment work, not evidence against the paper's reported cooperation results.

## Corrected landscape specification and scheduling evidence

The paper's section3.10 explicitly permits multiple seeds per cell.
Our observed piles above four units therefore do not establish a model discrepancy.
Note5 instead specifies exactly250 seeds of each maximum size1,2,3,4: 1,000seeds and2,500sugar units.
The observed1,015seeds fail that initialization requirement despite matching total sugar.
The configuration map now separates this required correction from allowed multi-seed occupancy.

Notes3 and7 clarify sequential execution within cycles and randomized agent ordering between cycles.
For COM1, a later reader cannot receive a message already removed by an earlier reader.
The recovered one-subcycle branch executes each agent's complete rule list in randomized order; it is a candidate for this documented schedule.
Historical rule order and message removal semantics remain unverified. No simulation rules were changed by this specification correction.

A renewed source search did not recover version1.2.3. The Internet Archive index returned a temporary-offline page.
The recovered newer source remains available, and a declared implementation of the paper specification can proceed without claiming historical byte equivalence.

## Balanced landscape reconstruction

`run_pilot.py ARCHIVE JDK NEW_OUTPUT balanced-landscape SEED` explicitly reconstructs the equal seed composition specified in section3.10 and note5.
It retains the controlled random generators, sets richness1.0, and replaces only the uniform-size seed-generation branch in the extracted source.
The size order is1,2,3,4 with250seeds each; native redistribution selects their cell locations.
This declared ordering and its random-stream consumption are reconstruction choices, not recovered historical details.
Other simulation rules and the default100-cycle pilot configuration remain unchanged.

[Two complete native workflows](results/balanced-landscape-2026-10-16/audit.json) produce identical bytes across all ten output files and validate1,400scalar observations.
The initialized world has exactly250seeds of each size,1,000seeds total, and2,500sugar units.
Its157multi-seed cells and115piles above four units are permitted by the specification.
Harvest priority, scheduling, communication semantics, other paper parameters, and full ensembles remain unfinished.

The observer reads seed composition without advancing the world or drawing random numbers.
It now belongs to the native model package to access the protected seed array without modifying source.
Compile it with `javac -cp CLASSES:LIB -d AUDIT_CLASSES replications/buzing_2005/LandscapeAudit.java`.
Run `java -Djava.awt.headless=true -Dreplication.seed=0 -cp AUDIT_CLASSES:CLASSES:LIB nl.vu.cs.sugarland.model.LandscapeAudit` from a fresh directory containing the retained configuration.
Direct Java source launch uses a separate classloader and cannot access the protected field; both failed observer attempts remain in external evidence.

## Alone-first harvesting reconstruction

`run_pilot.py ARCHIVE JDK NEW_OUTPUT paper-harvest SEED` adds the paper's alone-first harvesting rule to the balanced-landscape variant.
An acting agent consumes an accessible pile alone even when other agents occupy the cell.
A pile above its threshold is shared equally when multiple agents are present; a lone agent still requests help.
The threshold comparison retains the released maximum-harvest interpretation: amounts equal to the threshold are accessible.
Native resource removal and reseeding remain in the original lifecycle.

[Two full100-cycle runs](results/paper-harvest-2026-10-16/audit.json) produce identical bytes in all ten data files and validate1,400scalar observations.
The expanded observer verifies8,233accessible-pile events and11,080shared-pile events.
At each observed event it checks every colocated agent's exact native floating-point wealth update.
The expanded checks preserve all trajectories from the initial observer run. Both runs end with61agents.
This outcome uses the pilot's remaining defaults and is not a paper result or negative replication.
Scheduling, communication removal rules, remaining Table2 settings, and full experimental ensembles still require alignment.

## COM1 specification reconstruction

`run_pilot.py ARCHIVE JDK NEW_OUTPUT paper-com1 SEED` combines the balanced landscape and alone-first harvest with Table2 parameters and one-subcycle scheduling.
The candidate schedule runs each agent's full rule list before the next randomized agent, consistent with notes3 and7.
The original message-board getter already removes each received message when COM1 is enabled.
Our earlier inference from the caller alone was incorrect; the added deletion was redundant and has been removed.
The remaining observer checks native receive-time removal. Exact historical source remains unavailable.
Message expiry is disabled and removal on response is disabled for COM1.

[Two complete100-cycle workflows](results/paper-com1-2026-10-16/audit.json) validate1,400scalar observations and produce identical bytes across all ten output files.
The native lifecycle verifies6,459received-message deletions, each followed by an absence check.
Configuration checks cover every Table2 numeric setting, cooperation threshold1, mutation enablement, and message-removal flags.
Both runs end with299agents. The original seed0 here is a reconstruction seed, not an identified publication seed.
The full experiment horizon, all thresholds, ten-seed ensembles, COM0/COM2 behavior, and the cooperation denominator remain unfinished.

## Protocol execution and extinction handling

The runner accepts `paper-com0`, `paper-com1`, and `paper-com2`, with `--threshold 0..4` and an explicit `--cycles 1..5000` horizon.
COM0 sets both preference ranges to zero and disables mutation. COM2 retains messages until the listener reaches the requested cell.
All reconstructed conditions disable timed expiry and use the audited Table2 settings.
The native runner completes its requested horizon after extinction; these records are preserved, not dropped.
Its database writes zero for empty-population averages; those values must not be interpreted as surviving agents' gene preferences.

[The protocol checks](results/protocol-checks-2026-10-16/audit.json) retain one seed per condition.
COM0 and COM2 complete1,000cycles each, with final populations0 and767.
The corrected COM1 observer completes100cycles and reproduces all ten previous data files byte-for-byte.
This verifies14,700scalar observations without asserting paper-level agreement from single seeds.
The full experiment horizon, ten-seed ensembles, cooperation denominator, and remaining source-rule alignment still require validation.

## Cooperation measurements and full reconstruction ensemble

The released cooperation average is the mean agent flag, not the fraction of harvest actions.
The observer now records successful harvest events, shared harvest events, consumer participations, and shared consumer participations per cycle.
A shared event with three agents contributes one shared harvest event and three shared consumer participations.
The native agent-flag average remains available as a separate measurement. Ratios with no harvests or consumers are undefined.

[The1,000-cycle observer replay](results/metric-observer-2026-10-16/audit.json) preserves all ten native files byte-for-byte.
It records260,828harvest events, including128,589shared events, and390,146consumer participations, including257,907shared participations.
These are event totals, not independent samples.
COM0 now uses an always-false comparison after the existing random draw, preventing the original `<=0` boundary from permitting communication.

`run_ensemble.py ARCHIVE JDK NEW_OUTPUT` freezes its runner before executing150runs: three protocols, five thresholds, and seeds0–9, each for2,000cycles.
The horizon follows the inspected Figure4 population axis; the original publication seeds remain unknown.
The protocol declares comparisons before the ensemble runs and discloses that seed0 pilots were already observed.
All outcomes and native failures are retained in a flushed completion ledger; a failed command stops the ensemble.
Full analysis and historical-rule fidelity remain pending. This launched reconstruction is not a completed paper replication.

## Independent ensemble audit

`audit_ensemble.py RUN prefix|complete NEW_OUTPUT` validates the original150-condition grid, frozen runner hashes, source hashes, configurations, and native data checksums.
It independently reads seeds, thresholds, horizons, mutation flags, and removal settings from the actual configuration files.
Every run must contain2,000consecutive records in all scalar outputs and harvest counts, including all post-extinction observations.
The audit checks absorbing extinction, integer population, bounded preferences, and consistent harvest/participation accounting.
It reports undefined cooperation ratios and excludes empty-population gene placeholders from descriptive alive-agent averages.

[The first retained prefix](results/ensemble-prefix-2026-10-16/audit.json) contains four completed runs,56,000scalar observations, and8,000harvest-count records.
The snapshot remains incomplete and must not be counted as150runs.
[Negative controls](results/ensemble-prefix-2026-10-16/audit-controls/controls.json) verify rejection of both an incomplete ensemble in complete mode and a deliberately altered population file.
These controls are explicitly separated from scientific results. Complete mode requires all150runs and a successful final native-run ledger.
The observer validates accounting, not historical source equivalence or the paper's scientific claims.

## Reproduction fidelity audit

[A read-only newborn observer](results/birth-observer-2026-10-16/audit.json) completes1,000cycles and preserves all ten native data files byte-for-byte.
It checks49,792births for parental inheritance of vision, metabolism, death age, and fertility-start age, plus newborn age and sugar endowment.
All checks pass. Original and instrumented source hashes, the first-party observer insertion, native logs, and birth records are retained.

Fertility-end age differs from both parents in44,819births.
The source resets that attribute and draws it anew from the configured sex-specific range; reproduction passes only the fertility-start age.
The paper describes inheritance of child-bearing properties without resolving this distinction.
This remains a historical-fidelity question, not proof of an incorrect published conclusion.
The frozen150-run ensemble continues unchanged; no reproductive rule was selected to improve agreement.

## Validated removal of wall-clock pacing

The native model sleeps10milliseconds after every cycle, independently of its logical iteration clock.
`run_pilot.py ... --unpaced` removes only that sleep in the extracted experimental source.
[Paced/unpaced comparisons](results/unpaced-validation-2026-10-16) preserve all ten native output files exactly for COM0 at2,000cycles, COM1 at100cycles, and COM2 at1,000cycles.
The COM2 unpaced execution took2.84seconds. No simulation horizon, seed, rule, or logical clock was changed.
These checks cover seed0 at threshold0 for COM0 and threshold1 for COM1/COM2; other conditions require overlap checks.

A separately frozen accelerated150-run ensemble is now running. The original paced ensemble remains active and preserved.
The retained launcher differs only by declaring and passing `--unpaced`; its hashes and command are recorded.
Overlapping runs are paired validation data, not additional independent seeds. Neither ensemble is yet complete.

## Paired pacing audit and paper comparison gate

[All19completed overlapping runs](results/pacing-overlap-2026-10-16/audit.json) match exactly across all ten native output files.
The separately audited accelerated prefix covers18runs,252,000scalar observations, and36,000harvest-count records.
These snapshots were taken at different instants; paired duplicates do not increase unique seed coverage.
The accelerated ensemble remains in progress.

`compare_paper.py COMPLETE_AUDIT NEW_OUTPUT` requires all150audited runs and rehashes native data and event logs before producing grouped comparisons.
It compares the reported survival pattern across ten seeds for each protocol/threshold pair.
Approximate population and communication levels receive numerical differences, without inventing precision or acceptance margins.
Late summaries use cycles1501–2000; extinct populations contribute zero population but no invented gene preferences.
Both cooperation-event and consumer-participation ratios remain separate.
An18-run prefix is rejected before any comparison output is created.
This completion gate has been exercised; full comparison execution awaits the completed ensemble.
No automatic paper verdict follows from the table because historical-source and reproductive-rule questions remain.

## Complete reconstruction ensemble

[The complete audit](results/complete-ensemble-2026-10-16/audit.json) validates all 150 runs, 2,100,000 scalar observations, and 300,000 harvest-count records.
Each run completed 2,000 cycles. The terminal ledger reports exit code zero and 150 completed runs.
The compressed evidence archive retains every audited native output, configuration, manifest, and event log; its complete contents were verified against the audit snapshot.
Earlier prefix snapshots remain historical evidence, not additional independent runs.

[The survival comparison](results/complete-ensemble-2026-10-16/survival.csv) gives surviving seeds at cycle 2,000:

| Protocol | CT=0 | CT=1 | CT=2 | CT=3 | CT=4 |
| --- | --- | --- | --- | --- | --- |
| COM0 | 0/10 | 0/10 | 0/10 | 0/10 | 10/10 |
| COM1 | 0/10 | 1/10 | 10/10 | 10/10 | 10/10 |
| COM2 | 5/10 | 10/10 | 10/10 | 9/10 | 10/10 |

COM0 agrees with the reported survival pattern. COM1 at CT=1 and COM2 at CT=0 require further fidelity investigation.
The paper also qualifies population recovery as occurring in most cases; our per-seed pattern comparison is not a published deterministic acceptance test.
COM2 at CT=3 loses one seed and does not by itself establish a contradiction.
The comparison retains approximate population and gene-level differences without manufacturing precision or confidence bounds.
Unknown publication seeds, the newer recovered release, scheduling reconstruction, and fertility-end inheritance remain limitations.
**This remains an incomplete study, not a validated negative replication.**

[Trajectory plots](results/complete-ensemble-2026-10-16/plots) show all seeds, with extinct-agent preferences and undefined harvest ratios masked.
Separate panels retain native agent cooperation, shared harvest events, and shared consumer participations.
These denominators differ materially; they cannot be interchanged when comparing the publication's prose, monitor table, and figures.
Plot bounds include zero and one visibly. Colors identify seeds consistently, without treating paired pacing runs as additional samples.

To inspect the retained evidence, extract `audited-data.tar.gz` into a fresh directory, then run:

```sh
python replications/buzing_2005/compare_paper.py /extracted/audit /new/comparison
python replications/buzing_2005/plot_ensemble.py /extracted/audit /new/plots
```

Plotting requires NumPy and Matplotlib; retained plot metadata records the executed versions.
The full workflow generated six plots. An incomplete 107-run audit was rejected before creating plot output.

## Candidate fertility bounds: observed implementation error

The recovered `SugarAgent.selectPartners` compares a candidate's age with the initiating agent's fertility bounds.
The bundled class bytecode confirms the same receiver error; this is not merely a stale source comment.
Section 3.14 requires both parents to be within their fertile ranges.

[The native observer](results/parent-fertility-2026-10-16) records 103,457 births in COM2, threshold1, seed0, over 2,000 cycles.
In 3,926 births, the partner is outside its own fertile range: 3,330 below its minimum and 596 above its maximum.
All initiating parents are within their own ranges. All ten output files match the unobserved baseline exactly.
This demonstrates a recovered implementation mismatch, not a defect established in the paper's unavailable historical version.

`audit_parent_fertility.py BASELINE NEW_OUTPUT observe|own-range` verifies baseline source/configuration/data hashes and recompiles all native sources.
The `own-range` mode changes only the two candidate-bound receivers and adds the passive observer.
Three independent corrected COM2 workflows produce identical bytes in all ten files and final population738, versus751 in the baseline.
The corrected observer records 113,142 births, with zero out-of-range parents.
A corrected COM1 threshold1 seed0 workflow still becomes extinct and records 9,693 births with zero eligibility violations.
The complete workflows retain raw birth records, native outputs, source hashes, and logs.

A separately frozen 150-condition correction ensemble now repeats the entire baseline grid.
Its protocol discloses the observed pilots and fixes the correction before the ensemble outcomes.
It leaves fertility-end inheritance, other model rules, and all experimental parameters unchanged.
This diagnostic ensemble is not a completed paper replication or an additional distinct paper.

## Independent correction audit and sugar eligibility

`compare_parent_fertility.py ENSEMBLE prefix|complete NEW_OUTPUT` verifies paired baseline/corrected data, configurations, source hashes, fertility records, and harvest accounting.
It reverses only the two fertility edits and observer insertion, then requires exact equality to the baseline source.
[The retained prefix](results/parent-comparison-2026-10-16/prefix-comparison.json) validates 82 paired runs, 2,296,000 scalar observations, and 3,527,735 corrected births.
All corrected parents satisfy their own fertility ranges. Prefix groups report actual contributing seeds, without calling partial groups complete.
Complete mode rejects an incomplete grid. A separate altered-population control fails at its checksum before creating comparison output.

`audit_parent_fertility.py BASELINE NEW_OUTPUT observe --observe-wealth` also records sugar immediately before parental endowment is halved.
[The complete COM2 threshold1 seed0 replay](results/parent-comparison-2026-10-16/wealth-observer/audit.json) again preserves all ten baseline files exactly.
Of 103,457 births, 25,655 involve a zero-sugar parent; 3,475 involve two zero-sugar parents.
Both configured reproduction thresholds are zero. The recovered comparisons permit equality, while sections3.13–3.14 specify sugar above the threshold.
This is another recovered implementation/specification mismatch to isolate before interpreting scientific disagreements.
It does not establish that the unavailable historical implementation used this rule.
The running fertility-only ensemble remains unchanged; no sugar-eligibility correction has yet been applied.

## Strict positive-sugar reconstruction

`audit_parent_fertility.py BASELINE NEW_OUTPUT own-range-positive-sugar` additionally excludes equality at both reproduction sugar checks.
It retains the own-range fertility correction and observes each parent's sugar immediately before every birth endowment is halved.
All observed parents must exceed their own threshold. Configuration, seeds, mutation, scheduling, and other model rules remain unchanged.
This follows the paper's above-threshold requirement; it is not recovered historical code.

[Three diagnostic conditions](results/positive-sugar-2026-10-16/pilot-comparison.json) complete 2,000 cycles each.
COM2 at threshold1 ends at648agents, compared with738for fertility-only and751for the original reconstruction.
Its86,580births satisfy both eligibility rules. An independent repeat matches all ten files byte-for-byte.
COM1 at threshold1 and COM2 at threshold0 both become extinct, with7,789and8,244eligible births respectively.
These seed-zero pilots do not determine a paper-level verdict.

A frozen150-run strict-sugar ensemble is now running with the same grid as the original and fertility-only ensembles.
`compare_parent_fertility.py ... --correction own-range-positive-sugar` independently reverses exactly four rule edits and removes the two passive observer lines.
It requires exact equality to baseline source, unchanged configurations, valid raw data, and positive pre-halving sugar for every birth.
Its first seven pairs pass196,000scalar observations and33,591births. The snapshot is explicitly incomplete.
No rule or parameter was selected by optimizing agreement with the publication.

## Complete fertility-only comparison

[All150paired runs](results/fertility-complete-2026-10-16/comparison.json) pass the independent source, configuration, trajectory, birth, and harvest audit.
The audit reads4,200,000scalar observations across original and corrected conditions and11,494,812corrected births.
No corrected birth violates either parent's own fertility range. Both complete grids retain all extinct outcomes.

COM1 threshold1 survival changes from1/10to3/10. COM2 threshold3 changes from9/10to10/10.
COM2 threshold0 stays at5/10, but four paired seeds change survival status in opposite directions.
Other group survival counts remain unchanged. These paired differences measure implementation sensitivity, not independent additional replicates.
The correction does not resolve all discrepancies with the publication; sugar eligibility and historical fidelity remain separate questions.

Three compressed archives retain every corrected native trajectory, configuration, manifest, birth record, and event log.
Their complete contents were verified byte-for-byte against the external run evidence. Original author sources and compiled classes are excluded.
The original reconstruction and fertility-only evidence remain separate; the strict-sugar ensemble continues independently.

## Complete combined correction

[The strict-sugar audit](results/positive-sugar-complete-2026-10-16/comparison.json) validates all 150 runs and 9,161,420 births.
Every observed birth satisfies both parents' own fertility range and strictly positive pre-halving sugar.
The paired audit verifies 4,200,000 scalar observations across the original and combined-correction conditions.

[The three-condition survival table](results/positive-sugar-complete-2026-10-16/three-condition-survival.csv) preserves the same ten seeds in every condition.
COM1 threshold-one survival is 1/10 originally, 3/10 after fertility correction, and 1/10 with both corrections.
COM2 threshold-zero survival is 5/10, 5/10, and 2/10 respectively; threshold-three survival is 9/10, 10/10, and 10/10.
Other group survival counts are unchanged. These are implementation-sensitivity findings, not three independent paper replications.
Historical scheduling and inheritance remain unresolved, and the paper-level study remains incomplete.

Archives are split by protocol and threshold, with all ten seeds retained in each.
Every archived member was verified against the executed run. Source/classes are excluded; raw trajectories, configurations, birth and wealth records, logs, and manifests are retained.
