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
mating, inheritance, culture, combat, lending, trading, and disease.

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

## Original-suite execution

The historical Linux build completed under a two-core, 3 GiB, 90-minute limit.
All 35 enabled original tests passed with replay seed 20261017. Both test suites and
the original simulator compiled with GHC 8.4.4. The commands were:

```bash
stack build --test --no-run-tests --jobs 2
stack test SugarScape:sugarscape-test --test-arguments="--quickcheck-replay=20261017" --jobs 2
```

The original suites are executed unchanged. No new unit or integration tests are
introduced. [Native logs and the independent source/binary audit](results/original-suite-2026-10-17)
are retained. All 60 archived inputs remain byte-identical. The model-level suite
was compiled but not run, so there is no completed-study credit.

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
All three ensembles are running. Wealth index 0 completed first, and its remaining
worker starts at index 1; no duplicate input is counted. Each single-core worker
has a six-hour limit and retains interrupted output without crediting completion.

## Native exporter and independent audit

The [first completed outputs](results/native-first-2026-10-17) cover all three full
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
