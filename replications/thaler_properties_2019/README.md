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
are retained. All 60 archived inputs remain byte-identical. The model-level suite later reached its execution limit; see the retained timeout
evidence below. There is no completed-study credit.

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
completed all three scenarios with both corrections. The [initial launch](results/corrected-ensemble-launch-2026-10-17)
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

The original enabled model-test suite used replay seed 20261017 and its verified
historical binary. It reached the 1,800-second limit while displaying `Inheritance Gini`,
with exit code 124 and no completed assertion result. [The terminal state and log](results/model-suite-timeout-2026-10-17)
are retained. This is an incomplete execution, not a property failure. Six other model
properties remain disabled in the source.


## Complete corrected carrying-capacity ensemble

[All 100 corrected carrying trajectories](results/corrected-carrying-ensemble-2026-10-17)
pass independent audits across 8,521,865 agent observations. Mean population over times
101–400 is 204.921500, with a 95% interval of [203.705042, 206.137958]. The code's
204 target lies inside this interval; the appendix's 210 target remains outside.
The same-seed comparison retains the original 205.815833 mean. Source correction does
not explain the appendix's higher target or establish a completed negative replication.


## Seed-generator and source-history audit

The original property generator draws from the full signed `Int` range, whereas our
frozen protocol uses distinct positive 31-bit seeds. A [native generator audit](results/seed-generator-audit-2026-10-17)
records 100 draws from the pinned QuickCheck runtime and the resulting random states.
The source of `random-1.1` shows that `mkStdGen` converts to `Int32` and masks its sign
bit. Both seed ranges therefore map into the same effective 31-bit input space.
Our protocol excludes zero and samples without replacement; it does not omit a broad
second-generator state space. All 200 recorded random states match the source formula.

Two complete original 200-step simulations using a large native seed and its masked
equivalent produce byte-identical exports, each containing 50,000 agent records.
This closes the suspected high-bit state-space discrepancy without replacing any
ensemble or counting the equivalent runs as independent samples. It does not claim
that two different seed lists produce identical ensembles or explain target differences.

Git history also confirms that simulator and test code are unchanged between the
May 19 initial implementation and the pinned June 11 revision. Only the README and
validation PDF changed. This strengthens code provenance while leaving final-proceedings
text fidelity unverified.


## Complete corrected trading ensemble

[All 100 corrected trading runs](results/corrected-trading-ensemble-2026-10-17) are
independently audited across 6,163,442 agent observations. Indices 29 and 49 have fewer
than two final prices, so their sample standard deviations remain undefined.
The frozen primary audit retains both and emits no aggregate comparison.

Under the separately labelled author-library zero convention, mean dispersion is
0.0509942 and the one-sided 95% upper bound is 0.0582174, above the 0.05 target.
The individual predicate passes 64/100 runs, including source-defined zero values.
The paired change from the historical ensemble is +0.007340 with interval
[−0.004692, 0.019372]. This does not establish a correction effect or a paper-level verdict.
All three corrected quantitative ensembles are now complete and independently audited.

## Trade-on/off appendix comparison

A [separate frozen paired experiment](results/trade-control-first-2026-10-17/protocol.json)
uses `mkCarryingCapacityWithSpice` and `mkParamsFigureIV_6`. These original configurations
differ only in the trading flag. The first complete 1,000-step pair verifies identical
initial agents, cells, and summaries, plus the sole treatment difference in resolved parameters.
It contains 24,856 snapshot-agent observations and 4,269 snapshot-trade records.

The remaining 99 seeds per configuration are running separately from this first pair.
The one-CPU, 2 GiB worker has a three-hour limit and excludes the completed seed.
Measurements cover population, survivor vision and metabolisms, and sugar-wealth Gini.
Combined sugar-plus-spice inequality is reported separately. The 1,000-step horizon and
late window 801–1,000 are explicit study choices for the paper's qualitative statements.
No ensemble conclusion is claimed from the first pair.


## Mating and inheritance comparison

[Two complete first-seed trajectories](results/demographics-first-2026-10-17) use
`mkParamsAnimationIII_1` and `mkParamsFigureIII_7` through time 1,000. Independent
audit verifies 111,705 snapshot-agent observations, identical initial conditions, and
inheritance as the sole differing dynamics parameter. Final populations are 264 without
inheritance and 1,034 with inheritance; these are single-seed observations.

The remaining 99 seeds per configuration run in a separate one-CPU, 2 GiB worker,
with a three-hour limit. The frozen protocol records final sugar Gini, population, and
explicitly diagnostic late-window means. It distinguishes the book's 0.7 Gini target
from the appendix's reported approximately 0.35 inheritance and 0.21 no-inheritance values.
Reproducing the appendix's disagreement with the book would support this paper's result.
No ensemble conclusion or completed-paper credit follows from the first pair.

Restore the published CSV gzip files, then audit the first pair with:

```bash
python results/demographics-first-2026-10-17/audit_first.py \
  /path/to/first /path/to/protocol.json /path/to/new-audit.json
```


## Independent paired-ensemble audit

`audit_paired_observers.py` consumes the protocol, native observer/source directory,
a new output path, and one or more disjoint run directories. It verifies all source
and binary pins, original/gzip hashes, all summary times, snapshot populations and
wealth sums, paired initialization, and the sole treatment parameter. It reconstructs
Gini using ranked and pairwise formulas. Undefined outcomes remain explicit.

```bash
python audit_paired_observers.py /path/to/protocol.json /path/to/native-observer \
  /path/to/new-audit.json /path/to/first /path/to/remaining
```

Complete inference requires 100 pairs and matching completion ledgers. `--allow-prefix`
audits only available complete pairs, lists unpaired records as unaudited, and emits
no aggregate comparisons. It reads the published gzip files directly.

[Native first-pair audits and rejection evidence](results/paired-observer-audit-2026-10-17)
cover both experiments. The inheritance pair has final sugar Gini 0.352099 versus
0.222819 without inheritance. The trading pair has final sugar Gini 0.353110 versus
0.313486 without trading. These are single-seed measurements, not ensemble conclusions.
Both actual incomplete ensembles were rejected in full mode before output creation.
The complete-ensemble success path awaits all 100 pairs; no synthetic completion is used.


## Spice configuration comparison

[The first native book-parameter trajectory](results/spice-first-2026-10-17) uses
`mkParamsAnimationIV_1`, with vision 1–10 and sugar/spice metabolisms 1–5. Its
1,000-step audit verifies 9,511 snapshot-agent observations and all 60 source pins.
Population is 400 initially, 97 at time 100, 87 at time 500, and 85 at time 1,000.
It first falls below 90 at time 268. These are single-seed observations.
The [population plot](results/spice-first-2026-10-17/population.png) compares both
audited trajectories; its script and control-reuse receipt are included.

The existing `trade_off` experiment supplies the NetLogo-like comparison without
duplicate runs. Resolved scenarios confirm that only vision and the two metabolism
ranges differ, apart from labels. Both use the same 100-seed list and 1,000-step
horizon. Initial agents need not match because these configuration ranges differ.
The remaining 99 book-parameter seeds subsequently completed under a one-CPU,
2 GiB, three-hour limit; the full comparison appears below.

The appendix's approximate values of 105, below 90, and 97 remain descriptive
references. Full ensemble results must report trajectories and uncertainty without
inventing an equivalence tolerance. This first trajectory does not complete A10.

## Combat replacement fidelity

The appendix describes age-death replacement in Animation III-11. The pinned
`Agent.handleTick` sends both starvation and old age to `agentDies` (Agent.hs:116).
That function invokes `birthNewAgent` whenever replacement is enabled (Dying.hs:24).
`handleKilledInCombat` instead calls `kill` directly (Move.hs:134). Thus combat deaths
bypass replacement, while both starvation and age deaths permit it.

Keep this code/prose distinction in combat experiments. Existing summary output
does not record death causes or attacker/victim events, so population curves alone
cannot prove the appendix's causal or single-invader claims. No combat verdict follows
from source inspection.


## Spice ensemble audit and frozen prefix

`audit_spice.py` accepts the frozen spice protocol, native observer/source directory,
a new output path, `--book` run directories, and `--control` run directories.
It verifies source and binary pins, all raw/gzip hashes, population timelines,
snapshot totals and wealth sums, absence of trading, and the three parameter-range
differences. Matched seeds do not imply identical initialized agents.

[The frozen prefix](results/spice-prefix-audit-2026-10-17) independently validates
17 matched seeds and 372,808 snapshot-agent observations. Published gzip-only
exports reproduce every result exactly. Captured ledgers remain fixed while native
workers continue; records outside these matched seeds are explicitly unaudited.

Without `--allow-prefix`, all 100 seeds must be available for each selected scenario.
A completed trade-off cohort can be audited while its separate trade-on cohort still
runs. The actual incomplete data is rejected before output creation in full mode.
The 100-pair spice success path is now verified by the full audit below. Prefix mode
emits no comparisons.
Full comparisons report population at 100, 500, and 1,000, the mean over 801–1,000,
and same-seed book-minus-control changes, with 95% intervals across 100 runs.
First crossings below 90 and never-crossed cases remain explicit per seed.


## Combat event-trace diagnostic

[A separately instrumented diagnostic build](results/event-trace-diagnostic-2026-10-17)
logs attacks, delivered combat events, deaths, and births. The only source changes
add observations in `Agent/Common.hs` and `Agent/Move.hs`; all 58 other archived files
and the observer remain unchanged. Original outputs remain preserved.

Five complete paired controls use seed 602352629: wealth through 200, carrying
capacity through 400, trading through 1,000, and both combat scenarios through 1,000.
All 25 exported reference/trace files are byte-identical, including 445,491 agent
observations. The independent audit reconstructs active agent IDs from events and
checks every step against original trajectories. Event time precedes the simulator's
time increment, so events at time t account for the population at time t+1.

The cultural-combat trajectory has 16 kills and ends with 186 agents. The replacement
trajectory has 389 combat kills and ends with 11 agents. It replaces 435 starvation
deaths and 476 age deaths, confirming the code/prose replacement distinction. This
1,000-step diagnostic does not establish or refute eventual convergence to one agent.

All 405 attacks have positive computed combat rewards. In every case, the attacker's
wealth rises only by the harvested resource, never by harvest plus the computed
reward. The culture scenario computes 6,168 reward units; the replacement scenario
computes 773. `agentCombat` returns this reward in its income value, but does not add
it to the attacker's stored sugar. `handleTick` uses the returned value for net income
and pollution accounting. Neither combat configuration enables loans or pollution.

This is a released-source defect that can affect the claimed combat dynamics. It is
not a validated negative replication or evidence that a corrected model produces
single-agent invasions. Preserve the historical runs and compare any correction
separately, using the same seeds and independently verified event accounting.

The diagnostic contains the exact source overrides, diff, protocol, compiler log,
launch command, raw gzip exports, event logs, and auditor. Restore CSV files from gzip
and rebuild the pinned original and instrumented source directories before running:

```bash
python audit_events.py /path/to/instrumented-root /path/to/original-observer /path/to/new-audit.json
```

No new unit or integration tests were added; these checks exercise complete native
trajectories. The event trace is not used as performance evidence.


## Reward-only combat correction

[A separate post-hoc diagnostic](results/combat-reward-diagnostic-2026-10-17) credits
computed combat reward to stored sugar and refreshes occupier metadata before the
victim event. These experiments use the paper's sugar-only combat configurations.
The correction preserves the indexing and observation behavior to isolate reward
credit. The exact two-line addition is checked against the traced historical source.

All three non-combat controls remain byte-identical, covering 200,454 agent observations.
Both combat scenarios start identically to their historical counterparts. The independent
audit verifies 436,699 corrected/control agent observations and every-step birth/death
accounting. All 423 attacks credit harvest plus computed reward. Historical evidence
remains unchanged.

| First-seed measurement through 1,000 | Historical | Reward corrected |
| --- | ---: | ---: |
| Cultural-combat kills | 16 | 28 |
| Cultural-combat final population | 186 | 176 |
| Cultural-combat largest individual kill count | 2 | 6 |
| Replacement-combat kills | 389 | 395 |
| Replacement-combat final population | 11 | 5 |
| Replacement-combat largest individual kill count | 7 | 42 |

These descriptive differences do not establish an ensemble effect or spatial invasion.
Neither 1,000-step endpoint establishes eventual single-agent convergence.

[A frozen 100-seed comparison](results/combat-ensemble-launch-2026-10-17) now runs both
combat scenarios under historical and reward-corrected rules. Four completed first-seed
trajectories are retained at snapshot stride one. Two workers execute only seeds 1–99
at stride ten, preserving every event and every-step population summary. Each worker
has one CPU, 2 GiB, a three-hour budget, and a 4 GiB free-disk guard.

The 1,000-step horizon is an explicit diagnostic choice because the appendix gives no
fixed combat horizon. Primary measurements include population trajectories, causes of
death, replacements, kills per attacker, reward accounting, and first single-agent
occurrence, retaining never-reached cases. All 100 seeds are required for aggregate
comparisons. Spatial front and invasion claims require additional event analysis.

The [independent cohort audit](results/combat-ensemble-prefix-2026-10-17) passes on
24 matched cultural-combat pairs and the retained replacement-combat pair: 50 runs
and 1,410,778 snapshot agent observations. It reconstructs population at every step,
checks IDs at every exported snapshot, and verifies reward accounting and paired
initial conditions. Frozen ledger copies prevent later worker progress from changing
the audited input set. Prefix mode emits no aggregate comparisons. Full mode rejects
the actual unfinished cohorts; its success path awaits all 100 pairs per scenario.

`audit_correction.py ROOT ORIGINAL_OBSERVER NEW_OUTPUT HISTORICAL_TRACE` checks the
exact correction, unchanged controls, matched initialization and corrected event
accounting after rebuilding source trees and restoring the archived CSV files.


## Complete original spice comparison

[All 100 matched seeds](results/spice-ensembles-2026-10-17) now pass independent
audit: 200 runs and 2,223,578 snapshot-agent observations. The extracted gzip-only
archive reproduces every result and aggregate comparison exactly.

| Population measurement | Book settings, mean [95% interval] | NetLogo-like settings, mean [95% interval] |
| --- | --- | --- |
| Time 100 | 107.19 [105.93, 108.45] | 127.22 [125.76, 128.68] |
| Time 500 | 95.89 [94.87, 96.91] | 111.12 [109.71, 112.53] |
| Time 1,000 | 91.84 [90.82, 92.86] | 108.01 [106.46, 109.56] |
| Within-run mean, 801–1,000 | 92.52 [91.50, 93.54] | 108.33 [106.81, 109.86] |

At time 1,000, the same-seed book-minus-control mean difference is −16.17, with
95% interval [−18.01, −14.33]. No population becomes extinct. Only 26/100 book-setting
runs fall below 90 by time 1,000; none of the control runs do. The remaining cases
stay explicit rather than being dropped from crossing-time analysis.

The [population figure](results/spice-ensembles-2026-10-17/population.png) shows means
and pointwise intervals. These measurements differ from the appendix's approximate
below-90 and near-97 descriptions. They do not establish equivalence or a validated
negative replication. The initial source defects and independent implementation
fidelity still require investigation. The original dataset remains unchanged.

A [separate source-correction cohort](results/spice-corrected-first-2026-10-17) uses
the previously validated coordinate-index and observation corrections. The first
full pair passes the same audit with `--variant corrected`; the remaining 99 seeds
per configuration run under one CPU, 2 GiB, and a three-hour cap. Its first-seed final
populations are 82 and 102, compared with historical 85 and 103. No corrected ensemble
conclusion follows from that pair.

The extended auditor reproduces all 100 historical results exactly in original mode.
The archived original-only auditor is also retained beside its protocol, preserving
its original hash. No completed-paper credit follows from this partial appendix result.

## Migration and pollution spatial diagnostics

[Three complete 1,000-step diagnostic trajectories](results/spatial-diagnostics-2026-10-17)
cover original migration, migration with vision range 1–15, and original pollution.
They contain 303 spatial snapshots, 49,526 agent observations, and 772,953 cell
observations. Every snapshot reconciles with the corresponding summary.

Two additional native controls prove that denser cell exports preserve the original
agent records, summaries, trades, resolved parameters, and endpoint cells exactly.
All 60 historical model files remain unchanged. The published compressed exports
reproduce the audit exactly. The [migration figure](results/spatial-diagnostics-2026-10-17/migration.png)
separates occupancy from pre-event agent observations; the
[pollution figure](results/spatial-diagnostics-2026-10-17/pollution.png) uses a common scale.

These first-seed diagnostics do not establish the appendix's qualitative claims.
Coordinate aliasing remains present. Weaver implementation fidelity, corrected-source
sensitivity, and explicit qualitative comparisons remain outstanding.

## Disease persistence: completed source runs expose a configuration mismatch

[Both 100-seed persistence cohorts](results/disease-persistence-ensembles-2026-10-17)
are complete and independently audited. At step 1,000, each version has 81 infected-majority
runs and 16 runs with no infected agents. No population becomes extinct. Both source
and prose majority criteria pass 81/100, with exact binomial 95% interval [0.7193, 0.8816].
The 200 trajectories contain 894,627 snapshot agent observations; compressed-data
readback reproduces both complete audits exactly.

These are not faithful 25-disease negative replications. The scenario declares
25 diseases of maximum length 10, but `generateDiseaseMasterList` reverses those
tuple fields. All 400 saved disease configurations confirm that both V-1 and V-2
generate ten entries; V-2 increases maximum length to 25. The coordinate and
observation corrections leave this defect unchanged.

[A separate bounded correction validation](results/disease-count-correction-launch-2026-10-17)
aligns the generator with the declared field order. It must preserve the V-1 control
byte-for-byte before the intended 25-entry experiment expands. Those controls now
pass, as documented below; the historical cohorts remain preserved.

## Disease-count correction: validated controls and retained first seeds

[Four complete native runs](results/disease-count-correction-2026-10-17) verify the
two-line generator correction. Both V-1 controls reproduce all baseline exports
exactly. All other 59 model files and the observer remain unchanged relative to
each baseline. The four trajectories contain 10,689 agent observations, and
published compressed-data readback reproduces the independent audit exactly.

For the first V-2 seed, both corrected configurations generate 25 entries of length
1–10, comprising 24 distinct diseases. Infection clears by step 69 with count-only
correction and step 61 with combined coordinate/observation/count corrections.
Neither first-seed result establishes an ensemble outcome.

[The remaining 99 seeds per version](results/disease-count-ensemble-launch-2026-10-17)
run sequentially under one CPU, 2 GiB, and a three-hour outer cap. First-seed outputs
are retained rather than rerun. The observer auditor accepts an explicit
`--interval 1 100` for these remaining runs, requires the entire interval without
`--allow-prefix`, and emits no 100-seed inference from 99 runs. Its default full-run
mode reproduces the historical 100-seed disease audit exactly. Final inference
still requires reconciliation with the retained first seed.

## Independent NetLogo candidate: historical runtime execution

[The recovered candidate and exact replay](results/weaver-candidate-runtime-2026-10-17)
complete 1,000 steps using unchanged model code under NetLogo 4.0.4 and OpenJDK 11.
The external experiment selects spice preset 4 and seed 602352629. Population is
123 at step 100, 111 at step 500, and 104 at step 1,000.

Independent checks reconcile all 1,001 timestep records and 115,703 agent observations.
Both runs agree exactly except for timestamp metadata, and compressed-data readback
reproduces the audit. This is one unique input plus a replay.

The University of Bologna catalog attributes the gist's original community URL to
Iain Weaver, while Colgate preserves a later modified port linked to Leicester.
Source URLs, hashes, runtime pins, commands, and the failed initial XML attempt
are retained in the evidence. Byte identity with the 2009 publication and historical
Java-runtime parity remain unverified. This execution proof is not a completed
independent replication or an additional paper.

## Paired-observer ledger preservation

[Native first-pair audits](results/paired-ledger-snapshots-2026-10-17) now retain
immutable copies of the exact completion ledgers alongside their hashes. Trade and
inheritance results match the earlier audits. Full-mode checks reject both incomplete
cohorts before writing reports or ledger snapshots. No simulation settings changed;
full 100-pair results remain pending.

## Trade controls: complete 100-pair ensemble

[All 200 original-source trajectories](results/trade-paired-ensembles-2026-10-17)
complete 1,000 steps with matched initial conditions and trading as the only
configuration difference. The full audit reconciles hashes, sampled agents,
resource totals, trade records, and independent Gini calculations. Compressed-data
readback reproduces every scientific report field exactly.

| Step-1,000 measurement | Trade off | Trade on | Paired change, 95% interval |
| --- | ---: | ---: | --- |
| Population | 108.01 | 122.10 | +14.09 [13.24, 14.94] |
| Mean vision | 3.9710 | 3.8770 | −0.0940 [−0.1073, −0.0807] |
| Mean sugar metabolism | 1.5870 | 1.6336 | +0.0466 [0.0385, 0.0546] |
| Mean spice metabolism | 1.5769 | 1.6211 | +0.0442 [0.0368, 0.0515] |
| Sugar Gini | 0.3057 | 0.3383 | +0.0326 [0.0294, 0.0358] |
| Combined-wealth Gini | 0.2582 | 0.2958 | +0.0376 [0.0346, 0.0405] |

Late population, averaged over steps 801–1,000, increases by 14.0946 agents
[13.2368, 14.9524]. The [population figure](results/trade-paired-ensembles-2026-10-17/population.png)
shows complete trajectories and their paired differences with pointwise intervals.

Population and survivor-trait directions agree with appendix A.11 under the released
Figure IV-6 configuration. Inequality increases under both recorded definitions,
but these are diagnostics: the source has no distinct Figure IV-13 constructor.
Original coordinate and observation defects remain, and corrected-source sensitivity
is still needed. These results do not complete the entire paper.

## Corrected trade sensitivity with reused controls

[The first corrected pair](results/trade-corrected-first-2026-10-17) validates
matched initial states, the sole trading-flag difference, and all recorded outputs.
Population at step 1,000 is 102 without trade and 121 with trade. This single pair
supports no ensemble inference. Compressed-data readback reproduces the audit.

The remaining 99 trade-on inputs run under one CPU, 2 GiB, and a three-hour cap.
No-trade outputs come from the already running corrected spice cohort, avoiding
100 duplicate simulations. Both cohorts use the same frozen seeds and corrected
coordinate/observation implementation; source, observer, and binary hashes must match.

`audit_paired_observers.py --reuse-control CONTROL_PROTOCOL CONTROL_RUNS...`
checks the pinned control protocol and preserves original manifests and ledgers.
It explicitly excludes the spice-book scenario from trade inference. Full mode
requires all 100 pairs. The actual first-pair full-mode invocation rejects incomplete
coverage, while the historical original 100-pair scientific report remains identical.

## Corrected spice: complete cohorts and source sensitivity

[Both corrected 100-seed cohorts](results/spice-corrected-ensembles-2026-10-17)
are complete: 200 trajectories and 2,231,185 snapshot agent observations.
The full independent audit and compressed archive readback agree exactly.

| Population | Book settings, mean [95% interval] | Alternative settings, mean [95% interval] |
| --- | --- | --- |
| Step 100 | 107.62 [106.33, 108.91] | 126.83 [125.41, 128.25] |
| Step 500 | 96.60 [95.61, 97.59] | 111.25 [109.76, 112.74] |
| Step 1,000 | 92.23 [91.24, 93.22] | 108.32 [106.70, 109.94] |
| Steps 801–1,000 | 92.8656 [91.8785, 93.8527] | 108.6096 [107.0125, 110.2068] |

The final paired book-minus-control change is −16.09 agents [−17.97, −14.21].
Thirty-one book-setting runs cross below 90 by step 1,000; no alternative-setting
run does. Neither configuration becomes extinct. The
[population figure](results/spice-corrected-ensembles-2026-10-17/population.png)
shows the full and late trajectories with pointwise intervals.

[Same-seed source comparisons](results/spice-corrected-ensembles-2026-10-17/source-sensitivity.json)
estimate the combined coordinate/observation corrections. Final population changes
by +0.39 [−0.076, 0.856] under book settings and +0.31 [−0.272, 0.892]
under alternative settings. At step 500, the book-setting change is +0.71
[0.238, 1.182]. These are pointwise intervals, not simultaneous or equivalence tests.

The corrections do not bring the alternative-setting mean near the appendix's
approximately 97-agent description. No numerical equivalence tolerance was supplied,
so these measurements remain explicit rather than inventing a pass/fail boundary.
Independent reference fidelity and other appendix categories still prevent a whole-paper verdict.
The completed alternative-setting outputs also supply all corrected trade-off controls.

## Disease-count reconciliation: retained seed plus remaining inputs

[The reconciliation auditor](audit_disease_count_ensemble.py) verifies pinned native
sources and binaries, rechecks the retained first-seed files, and invokes the independent
trajectory auditor for indices 1–99. It checks every resolved pool has 25 entries
of length 1–10 and reports distinct counts separately. It recomputes final infection
predicates and clearance times from complete summary trajectories.

[Validation on 62 actual inputs](results/disease-count-reconciliation-2026-10-17)
reconciles 276,344 agent observations. All 62 count-corrected trajectories end with
zero infected agents and surviving populations. Their pools contain 19–25 distinct
diseases. These are partial results, not a full-cohort negative replication.

Frozen compressed-data readback reproduces the complete merged audit exactly.
Full mode rejects the actual incomplete cohort before creating an output directory.
Its successful 100-input path remains unverified until the real remaining runs finish;
prefix mode never emits confidence intervals. The combined-correction cohort remains
separate, and no first seed or no-trade control is rerun.

```sh
python audit_disease_count_ensemble.py PROTOCOL NATIVE_HOME FIRST_AUDIT RUN OUTPUT --allow-prefix
```

Omit `--allow-prefix` only after the 99-input worker produces its completion marker.
The retained first audit is the pinned `audit_disease_count_correction.py` output;
its source-fidelity controls and raw files remain linked evidence.
