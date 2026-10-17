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
All three historical ensembles completed all 100 runs.
Wealth index 0 and indices 1–99 ran separately; no duplicate input is counted. Each single-core worker
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

## Complete wealth ensemble

[All 100 native outputs and the independent audit](results/wealth-ensemble-2026-10-17)
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

[All 100 native outputs and the independent audit](results/carrying-ensemble-2026-10-17)
cover 40,000 steps and 8,550,893 agent observations. Mean population over times
101–400 is 205.815833, with a 95% confidence interval of [204.654564, 206.977102].
Neither the code's target of 204 nor the appendix's target of 210 lies inside it.
This is an unresolved quantitative difference, subject to the source issues below.

## Complete trading ensemble

[All 100 native outputs and the independent audit](results/trading-ensemble-2026-10-17)
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

## Observer validation and spatial discrepancies

[Observe.hs](Observe.hs) calls the unchanged historical simulator and exports agent,
trade, disease, culture, environment, and occupancy measurements. It selects the
scenario constructor directly, avoiding the CLI's duplicate scenario-name ambiguity.
[Native evidence](results/observer-2026-10-17) covers three complete trajectories.
The independent comparison matches all 199,604 shared agent records and 21,702 trades
exactly against the original exporter. All 60 archived source files remain unchanged.

The first spatial audit incorrectly assumed a 50×50 grid. That failed assumption and
its superseded report remain preserved. The source explicitly declares 51×51.
Two source behaviors explain why the stronger spatial check cannot pass as written:

- `Discrete.coordToIdx` uses `y * (xDim - 1) + x`. On the declared grid, 2,601
  coordinates map to 2,551 indices. Each row boundary aliases two distinct coordinates.
  Initial occupancy omits 2 of 250 wealth agents, 6 of 400 carrying agents, and 2 of
  200 trading agents for seed 602352629.
- `Agent.agentMsf` constructs observables from pre-event `s`, although the event
  returns updated `s'`. Environment occupancy and exported agent observables therefore
  describe different moments. Comparing their positions at the same timestamp is invalid.

The observer has not corrected either behavior. Disease, cultural, and spatial claims
must distinguish original observations from actual post-event state. No spatial or
whole-paper negative verdict follows from these checks.

The terracing property has additional source/prose differences: `drop 50` chooses time
51 as its baseline, and `onTheEdge` returns true when every neighbor has the same level.
Preserve both the source predicate and the prose criterion in subsequent measurements.
The appendix's A10 concerns spice. The paper separately mentions lending, but its
`src/test/Agent/Lending.hs` contains only a TODO; no implemented lending property exists.

Reproduce the observer comparison after restoring the historical source and native
outputs into the directories used by the original launch:

```bash
python replications/thaler_properties_2019/audit_observer.py \
  /path/to/observer-output /path/to/ensemble-outputs --output /path/to/new-audit.json
```

The observer directory must contain `source/` at the pinned revision and uncompressed
CSV files. Ensemble directories must contain the three original seed-602352629 exports.
The independent audit checks the complete trajectories, not isolated model functions.

## Paired source diagnosis

[Nine complete native trajectories](results/sensitivity-2026-10-17) isolate the
indexing correction, the observation correction, and both together. Each variant uses
seed 602352629 for the original 200-, 400-, and 1,000-step scenarios. Source comparison
verifies exactly the declared substitutions; the observer is unchanged.

The observation-only variant preserves every population, environment-sugar,
environment-spice, and pollution measurement at every timestep. Final coordinate
mismatches fall from 217/187/47 to zero for wealth/carrying/trading. The indexing-only
variant restores all 2,601 coordinates and initial occupiers, but retains the observation
lag. Combining both corrections restores the grid and eliminates final position mismatches.

These changes affect measured outcomes. For the trading trajectory, corrected indexing
alone gives 61 surviving agents; observation-only retains the original 57. Combining
both yields 61 agents and final observed price standard deviation 0.181524. One seed
cannot establish a population-level result or resolve a paper claim.

A [separately labelled 100-seed sensitivity ensemble](results/corrected-ensemble-recovery-2026-10-17)
is running all three scenarios with both corrections. The [initial launch](results/corrected-ensemble-launch-2026-10-17)
failed before producing runs because parallel Stack path resolution raced package-database
initialization. Recovery builds the full original component set and verifies the executable
path serially before starting workers. It retains the historical
ensemble's seeds, horizons, targets, and statistics. Its protocol explicitly labels
post-hoc source correction and preserves the original outputs and failures.
The container is limited to three CPUs, 4 GiB, and 7,500 seconds; workers have 7,200-second
limits. No corrected-ensemble result is claimed before complete independent audits.

Reproduce the paired diagnosis against complete native outputs and their source trees:

```bash
python replications/thaler_properties_2019/audit_sensitivity.py \
  /path/to/sensitivity-output /path/to/original-observer-output \
  /path/to/protocol.json --output /path/to/new-audit.json
```

Recovery passed its serial build gate. The first three corrected CLI exports match
the earlier corrected observer exactly across 204,191 agent records and 28,581 trades.
Their raw files, hashes, manifests, and comparison report are retained with recovery evidence.


## Remaining observer ensembles

A [frozen protocol](results/observer-ensemble-launch-2026-10-17/protocol.json) now covers
100 seeds each for terracing, disease clearance, disease persistence, and cultural dynamics.
Two independent workers run the original and corrected variants, respectively. Each
worker has one CPU, 2 GiB, and a three-hour limit; completed-run ledgers retain hashes.
The original source outputs remain pre-event observations. Corrected outputs are labelled
sensitivity evidence. Source and prose predicates remain distinct, including disease
majority rounding, cultural-balance asymmetry, and terracing's inverted edge predicate.
No result or completed-study credit is claimed for these running ensembles.


## Complete terracing ensembles

[Independent audits and all native outputs](results/terracing-ensembles-2026-10-17)
cover 100 original and 100 corrected runs, each through time 100. They verify
2,521,229 original and 2,525,538 corrected snapshot-agent observations, including initialization.
The original results distinguish the released predicate from the appendix prose:

| Original-source measurement | Mean | 95% interval |
| --- | ---: | --- |
| All four neighbors have the same sugar level | 0.453547 | [0.448670, 0.458423] |
| At least one neighbor has a lower sugar level | 0.543573 | [0.538671, 0.548475] |
| Position stability after time 50 | 1.000000 | Zero observed variance |

The 0.45 target lies inside the interval for the code's uniform-neighbor predicate,
but outside the interval for the prose's edge predicate. Every measured agent remains
stationary after time 50. Source stability also equals one when using its time-51 baseline.
`StatsUtils.tValue` returns `Nothing` for zero variance; `prop_terracing` then defaults
to pass. That is not statistical evidence for equality to its numerical target of 0.95.

With both source corrections, the uniform-neighbor ratio is 0.458383 and the prose edge
ratio is 0.538568; stability remains one. This preserves the successful stationary-agent
behavior while identifying which measured quantity supports the paper's 45% statement.
The remaining appendix outcomes and whole-paper verdict are still pending.

`audit_observer_ensemble.py RUN PROTOCOL SCENARIO NEW_OUTPUT` independently reconstructs
cell lookup, source/prose predicates, and statistics from raw CSV exports. Published
folders retain gzip copies; restore their CSV files before auditing. Completion requires
all 100 seeds for the selected scenario. `--allow-prefix` emits no confidence intervals.
The archived runner is byte-identical to the executed version; its manifest pins its hash.


## Complete corrected-wealth sensitivity ensemble

[All 100 corrected outputs and their audit](results/corrected-wealth-ensemble-2026-10-17)
cover another 5,000,000 agent observations. The original outputs remain unchanged.
Both source substitutions were fixed before these runs; seeds, horizon, and targets
match the historical ensemble. This is a source-correction diagnostic.

| Metric | Corrected mean | Corrected 95% interval | Exact target inside |
| --- | ---: | --- | --- |
| Gini | 0.485025 | [0.482307, 0.487744] | No |
| Skewness | 1.533518 | [1.503178, 1.563857] | No |
| Excess kurtosis | 2.132933 | [1.990235, 2.275631] | Yes |

[Paired effects](results/corrected-wealth-ensemble-2026-10-17/paired-effects.json)
compare the same 100 seeds. Mean changes are +0.002688 Gini, −0.044265 skewness,
and −0.201788 excess kurtosis. The Gini and kurtosis change intervals include zero.
The skewness change interval is [−0.088059, −0.000470]. These exploratory comparisons
do not turn the paper's approximate values into proven equivalence or a negative verdict.
The corrections alter measurements but do not make all exact point targets agree.

`compare_ensembles.py ORIGINAL_AUDIT CORRECTED_AUDIT NEW_OUTPUT` requires two complete,
seed-aligned ensembles with every statistic defined. It rejects undefined outcomes
instead of silently dropping paired seeds. For the corrected native audit, use the
archived auditor beside its corrected protocol and source manifest; the historical
auditor intentionally rejects modified source hashes.


## Complete disease-clearance ensembles

[All 100 original and 100 corrected trajectories](results/disease-clear-ensembles-2026-10-17)
reproduce the stated clearance-before-100 behavior. No population becomes extinct.
First clearance occurs at times 10–40 in the original runs and 9–46 with corrections.
Independent inspection of the exported time-50 agent snapshots confirms zero infections
and a surviving population in every run, without relying solely on summary counters.
Both the code's time-100 predicate and the prose's before-100 criterion pass 100/100
in each variant. The exact binomial 95% interval is [0.963783, 1.0]; finite sampling
does not prove universal success. The disease-persistence scenario remains unfinished.

The original enabled model-test suite is now also running with replay seed 20261017,
using its already-verified historical binary. It covers inheritance and wealth only;
six other model properties remain disabled in the source. Its result is still pending.
