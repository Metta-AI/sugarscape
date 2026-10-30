# Thaler and Siebers (2019): Show me your properties

**Status: incomplete.** This study concerns the Sugarscape case study in
[the author's conference-paper preprint](https://www.researchgate.net/publication/333198243_SHOW_ME_YOUR_PROPERTIES_THE_POTENTIAL_OF_PROPERTY-BASED_TESTING_IN_AGENT-BASED_SIMULATION).
It is distinct from *A tale of lock-free agents*. The 2020 follow-up uses SIR and
is excluded from the Sugarscape study count.

## Artifacts and fidelity

[The original repository](https://github.com/thalerjonathan/haskell-sugarscape) includes
model code, property tests, plotting scripts, and `validating_sugarscape.pdf`.
Use historical revision `63b3e761b9ef0d861610b7ba232978406b89585b`, LTS 12.16,
GHC 8.4.4, and the pinned QuickCheck fork `9ccdcbb3eaad7fe96c08ea5ecbbdfe852615bd49`.
[The manifest](source-manifest.json) records all 60 archived file hashes.
The later 2021 revision changes the compiler snapshot and a comment; it is not used.

The recovered paper text is an author-uploaded preprint. Publisher access returned
403, so final proceedings fidelity remains unverified. The validation appendix is
preserved in the original Git revision and identified by SHA-256 in
[the source audit](source-audit.json).

## Required replication scope

Reproduce the Sugarscape environment and agent-property demonstrations, the full-model
statistical procedure, and the validation appendix's reported outcomes. Preserve all
published positive and negative outcomes rather than counting successful checks alone.
The appendix covers terracing, carrying capacity, wealth, migration, pollution,
mating, inheritance, culture, combat, spice, trading, and disease.

Each scenario needs a source-to-claim mapping, native output, independent measurement,
and an explicit outcome. The paper's 100-run statistical comparisons must retain
that sample size. Qualitative claims need predeclared observable criteria and
trajectory inspection. Missing configurations or unsupported claims remain unresolved.
SIR results are outside this Sugarscape-specific scope.

## Source discrepancies to resolve before verdicts

- Carrying capacity targets 204 in the code and 210 in the validation appendix.
- The registered model suite enables inheritance and wealth only; six existing model
  properties are commented out. Its internal replication count is ten, whereas the
  appendix describes 100-run comparisons.
- The disabled trading property checks one trajectory. It does not implement the
  paper's Algorithm 6, which aggregates 100 runs using a one-sided statistical test.
- The cultural-balance Boolean expression is asymmetric. Its effect on complete
  trajectories must be measured before interpreting a pass as agreement with the prose.

The [scenario catalog](scenario-catalog.json) also identifies a naming collision:
`mkParamsFigureIV_11` is labelled `Figure IV-10`. The CLI selects the first matching
name and reports an unknown name without failing its exit status. Confirm output
artifacts and scenario parameters, not exit status alone.

These findings are source discrepancies, not validated negative replications.
A successful default test suite cannot establish complete paper reproduction.

## Frozen quantitative ensembles

The [ensemble protocol](ensemble-protocol.json) fixes 100 distinct seeds before any
native ensemble output. The original CLI will export complete trajectories with
unchanged model code, retaining raw files, compressed copies, logs, and checksums.

| Scenario | Runs | Horizon | Measurement |
| --- | ---: | ---: | --- |
| Animation II-2 | 100 | 400 | Population mean over times 101–400; report both 204 and 210 targets |
| Animation II-3 | 100 | 200 | Final sugar-wealth Gini, skewness, and excess kurtosis |
| Figure IV-3 | 100 | 1,000 | Standard deviation of final-time observed trading prices |

Confidence intervals and source-defined checks will be reported separately.
Non-rejection is not proof of equality. Undefined statistics remain explicit;
no missing or failed runs will be silently dropped. These 300 runs address three
quantitative targets; the remaining case-study and appendix requirements remain.
All three historical ensembles completed all 100 runs.
Wealth index 0 and indices 1–99 ran separately; no duplicate input is counted. Each single-core worker
has a six-hour limit and retains interrupted output without crediting completion.

## Native exporter and independent audit

The [first completed outputs](https://github.com/Metta-AI/sugarscape/tree/70da776a9a0682e04a6cd1b30a1ac5af1864307a/replications/thaler_properties_2019/results/native-first-2026-10-17) cover all three full
horizons: wealth 200 steps/50,000 agent observations, carrying capacity 400/87,502,
and trading 1,000/62,102. Independent audits recheck raw hashes, commands, seeds,
all timestamps, unique agent IDs, finite measurements, and original source pins.
The wealth Gini agrees between ranked and pairwise formulas to less than 1e-12.
These are execution and extraction proofs, not 100-run statistical results.

`run_ensemble.py` runs a specified interval using the unmodified native CLI. Its
protocol argument must be beside `source-manifest.json`. For example:

```bash
python replications/thaler_properties_2019/run_ensemble.py \
  /path/to/historical-source replications/thaler_properties_2019/ensemble-protocol.json \
  wealth /path/to/new-output --start 0 --stop 100 --seconds 21600
```

The independent auditor uses NumPy 1.26.4 and SciPy 1.16.3. Published first-output
folders retain compressed raw exports; restore them with `gzip -dk` before auditing.
The gzip roundtrip and raw hashes were verified. Audit separate scenarios separately:

```bash
python replications/thaler_properties_2019/audit_ensemble.py \
  /path/to/first-interval /path/to/remaining-interval --output /path/to/new-audit
```

Without `--allow-prefix`, all 100 distinct indices and each declared interval's
completion marker are required. Prefix audits produce no confidence-interval claims.
The auditor preserves the source library's moment conventions and records zero/one-price
samples as undefined alongside its zero-standard-deviation convention.

## Complete wealth ensemble

[All 100 native outputs and the independent audit](https://github.com/Metta-AI/sugarscape/tree/70da776a9a0682e04a6cd1b30a1ac5af1864307a/replications/thaler_properties_2019/results/wealth-ensemble-2026-10-17)
cover 20,000 steps and 5,000,000 agent observations. The frozen comparisons are:

| Metric | Mean | 95% confidence interval | Target | Target inside interval |
| --- | ---: | --- | ---: | --- |
| Gini | 0.482337 | [0.479581, 0.485094] | 0.48 | Yes |
| Skewness | 1.577782 | [1.544532, 1.611032] | 1.5 | No |
| Excess kurtosis | 2.334721 | [2.176770, 2.492672] | 2.0 | No |

These intervals concern the unchanged historical implementation and the frozen seeds.
They do not establish equality, equivalence, or a completed negative paper replication.
Source defects and the paper's approximate targets require investigation first.
Compressed raw exports can be restored with `gzip -dk` and passed to `audit_ensemble.py`.

## Complete carrying-capacity ensemble

[All 100 native outputs and the independent audit](https://github.com/Metta-AI/sugarscape/tree/70da776a9a0682e04a6cd1b30a1ac5af1864307a/replications/thaler_properties_2019/results/carrying-ensemble-2026-10-17)
cover 40,000 steps and 8,550,893 agent observations. Mean population over times
101–400 is 205.815833, with a 95% confidence interval of [204.654564, 206.977102].
Neither the code's target of 204 nor the appendix's target of 210 lies inside it.
This is an unresolved quantitative difference, subject to the source issues below.

## Complete trading ensemble

[All 100 native outputs and the independent audit](https://github.com/Metta-AI/sugarscape/tree/70da776a9a0682e04a6cd1b30a1ac5af1864307a/replications/thaler_properties_2019/results/trading-ensemble-2026-10-17)
cover 100,000 steps and 6,083,587 agent observations. Six final snapshots have fewer
than two prices: indices 1, 6, 11, 31, 40, and 80. Their sample standard deviations
are undefined. The frozen audit retains all six and emits no aggregate comparison.

A separately labelled replay of the author library's zero-for-small-samples convention
uses all 100 runs. Mean standard deviation is 0.0436544; its one-sided 95% upper bound
is 0.0507357, above the 0.05 target. The individual-run predicate passes 67/100 runs,
including the six source-defined zero values. This does not resolve the undefined
statistic issue or establish a full-paper negative replication.

Across all three historical ensembles, 300 runs and 19,634,480 agent observations
are independently audited. The remaining appendix claims and source diagnosis remain.

Later source-correction and recovered NetLogo controls remain in the full record. They do not replace original-source measurements or establish whole-paper replication. Migration/pollution configuration and historical implementation identity remain unresolved.

## Preserved evidence

[The full experiment record](https://github.com/Metta-AI/sugarscape/blob/51f7750ba5f2a88bcb461e033002cddb222e4762/replications/thaler_properties_2019/README.md) retains dated runs, budgets, failures, source hashes, figures, and detailed controls. Existing histories, outputs, and checkpoints remain unchanged. Historical launch notes do not establish current job status. Restore archived raw inputs before rerunning an analysis, as described in that record.

## Archived run records

Primary runners, analysis code, fixed study inputs, source provenance, and study findings remain tracked.
Dated run directories, checkpoint notes, copied runners, and generated source readbacks are preserved in [the experiment archive](https://github.com/Metta-AI/sugarscape/tree/36592013feae1765e6d7755fc470d095ec17d4df/replications/thaler_properties_2019).
Regenerated evidence belongs in the ignored output directories.

Commands and provenance records may reference archived inputs or historical scripts. Restore those dependencies before running the corresponding analysis:

```sh
git restore --source=36592013feae1765e6d7755fc470d095ec17d4df --worktree -- REPOSITORY_PATH
```

Replace `REPOSITORY_PATH` with the required archived file or directory. The restore leaves the index unchanged and the restored evidence ignored. The [original evidence archive](https://github.com/Metta-AI/sugarscape/tree/70da776a9a0682e04a6cd1b30a1ac5af1864307a/replications/thaler_properties_2019) retains raw outputs removed in previous cleanups.
