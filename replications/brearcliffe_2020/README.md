# Brearcliffe and Crooks: Creating Intelligent Agents

[Completed method replication: qualified author-code result](https://github.com/Metta-AI/sugarscape/tree/c320930a8fd0d670694dc4694e69687555f406b9/replications/brearcliffe_2020/results/method-verdict-2026-10-20).
All 1,600 frozen runs and 32,001,600 observations pass native audits, with independent checks for all thirty-two cohorts.
Both parameter interpretations remain explicit. The outcome is mixed; no exact historical agreement or validated negative result is claimed.
The [final comparison](https://github.com/Metta-AI/sugarscape/tree/c320930a8fd0d670694dc4694e69687555f406b9/replications/brearcliffe_2020/results/sixteen-pair-parameter-comparison-2026-10-20) retains nineteen endpoints overlapping neither setting and twenty-seven unresolved targets.
See the verdict for recorder corrections, reconstructed settings, all claim analyses, and remaining historical limitations.

## Recover source inputs

The [tested source-recovery CLI](https://github.com/Metta-AI/sugarscape/tree/c320930a8fd0d670694dc4694e69687555f406b9/replications/brearcliffe_2020/results/source-recovery-2026-10-19) retrieves the exact author artifacts and verifies every archive member, including license and citation notices.
Use new output directories; mismatched downloads fail visibly and remain available for inspection.

```sh
python replications/brearcliffe_2020/fetch_sources.py /new/source-directory
python replications/brearcliffe_2020/prepare_ensemble.py \
  /new/source-directory/release/code/Creating_Intelligent_Agents.nlogo /new/prepared-directory
```

The resulting 1,602 files match the frozen preparation used by this study.
These commands prepare inputs only. Execution still requires the qualified NetLogo 6.1.1 runtime, matrix extension, and recorder described below.

## Native pilot

The [launch record](https://github.com/Metta-AI/sugarscape/tree/7e88337b66d19ef04756679e72da74a7a05f6ec4/replications/brearcliffe_2020/results/native-pilot-launch-2026-10-19) selects Rule M versus evolutionary computing, with combat, corner starts, replacement, and growback 1.
This pairing does not use the disputed reinforcement-learning hyperparameters.
A separate retained model copy replaces only `random-seed new-seed` with `random-seed 20261019`.
The original source remains unchanged. This fixed seed is prospective, not a recovered author seed.

`Replay.java` uses NetLogo 6.1.1 and its original bundled matrix extension.
It records initial state and every subsequent tick, with both populations and all fourteen figure statistics.
A complete run must contain 20,001 finite observations with consecutive tick values.
The pilot has a 600-second wall limit, 1 GiB Java heap, and 50 MiB output cap. Partial outputs remain evidence, without completion credit.
The first full pilot completed but failed recorder qualification. The [retained discrepancy and correction](https://github.com/Metta-AI/sugarscape/tree/c320930a8fd0d670694dc4694e69687555f406b9/replications/brearcliffe_2020/results/recorder-qualification-2026-10-19) show exact short-run agreement after isolating measurement randomness. The [full-horizon comparison](https://github.com/Metta-AI/sugarscape/tree/c320930a8fd0d670694dc4694e69687555f406b9/replications/brearcliffe_2020/results/full-recorder-qualification-2026-10-19) now agrees exactly on all 320,016 values across 20,001 observations.

Compile against the NetLogo application JARs, then run:

```sh
java -Xmx1g -Djava.awt.headless=true -cp 'DRIVER_DIRECTORY:NETLOGO/app/*' \
  Replay /absolute/seeded-model.nlogo 'Rule M' EC 20000 /new/trajectory.csv
```

Place the original symmetric map and the NetLogo 6.1.1 matrix extension beside the retained model copy.
The external bounded launcher and exact command are retained in the launch record.

The [all-pairing qualification](https://github.com/Metta-AI/sugarscape/tree/c320930a8fd0d670694dc4694e69687555f406b9/replications/brearcliffe_2020/results/all-pairings-qualified-2026-10-19) now passes: all 256,256 values match native BehaviorSpace through 1,000 ticks for all sixteen pairings. The [first frozen Rule M/EC input](https://github.com/Metta-AI/sugarscape/tree/c320930a8fd0d670694dc4694e69687555f406b9/replications/brearcliffe_2020/results/first-ensemble-input-complete-2026-10-19) completes and passes fresh archive audit; complete ensembles remain outstanding.

The [full learning-method comparison](https://github.com/Metta-AI/sugarscape/tree/c320930a8fd0d670694dc4694e69687555f406b9/replications/brearcliffe_2020/results/rl-full-qualified-2026-10-19) passes: all 320,016 values match native BehaviorSpace through 20,000 ticks for Q-Learning versus SARSA.
The [frozen ensemble preparation](https://github.com/Metta-AI/sugarscape/tree/c320930a8fd0d670694dc4694e69687555f406b9/replications/brearcliffe_2020/results/ensemble-preparation-2026-10-19) defines 800 runs for each parameter interpretation, with matched prospective seeds. Both preparations reproduce identical bytes; one released-code input has completed and passed independent audit.

The [Figure 3 digitization](https://github.com/Metta-AI/sugarscape/tree/c320930a8fd0d670694dc4694e69687555f406b9/replications/brearcliffe_2020/results/wealth-digitization-2026-10-19) recovers 30 visible endpoint intervals and leaves two occluded endpoints unresolved. Four last-row panel labels were corrected after checking plot titles; rejected labels remain documented.

A [bounded CPU host trial](https://github.com/Metta-AI/sugarscape/tree/c320930a8fd0d670694dc4694e69687555f406b9/replications/brearcliffe_2020/results/cloud-qualification-launch-2026-10-19) is queued to verify two complete trajectories before scaling the frozen ensembles.

The [first bounded dispatcher batch](https://github.com/Metta-AI/sugarscape/tree/c320930a8fd0d670694dc4694e69687555f406b9/replications/brearcliffe_2020/results/first-batch-complete-2026-10-19) completes both inputs and passes fresh archive audit. Released-code coverage is 3/800 inputs, including the earlier Rule M/EC input.

The [original local Rule M/Rule M batch](https://github.com/Metta-AI/sugarscape/tree/c320930a8fd0d670694dc4694e69687555f406b9/replications/brearcliffe_2020/results/rule-m-cohort-launch-2026-10-19) has ended. Its 40 successes and the two earlier controls give 42 complete seeds; the eight unfinished inputs are recovering remotely.

The [cohort analysis](https://github.com/Metta-AI/sugarscape/tree/c320930a8fd0d670694dc4694e69687555f406b9/replications/brearcliffe_2020/results/cohort-analysis-preparation-2026-10-19) is specified and rejects incomplete samples before producing means. [An independent R checker](https://github.com/Metta-AI/sugarscape/tree/c320930a8fd0d670694dc4694e69687555f406b9/replications/brearcliffe_2020/results/cohort-verification-preparation-2026-10-19) is prepared for all means, standard deviations, and bootstrap intervals. The complete Rule M/EC and Rule M/Rule M cohorts now pass the fifty-run summary, independent arithmetic check, and numerical comparison.

## Completion scope

All declared ensembles, independent cohort checks, storage readbacks, parameter comparisons and claim analyses are complete.
The [final method verdict](https://github.com/Metta-AI/sugarscape/tree/c320930a8fd0d670694dc4694e69687555f406b9/replications/brearcliffe_2020/results/method-verdict-2026-10-20) distinguishes implementation fidelity, directional findings and unresolved historical numerical agreement.
Original paper seeds and between-run uncertainty remain unavailable. Mislabeled, duplicated and unreadable figure segments remain unresolved.
Pointwise bootstrap intervals and raster overlap do not establish equivalence; the paper supplies no numerical equivalence margin.

## Complete-cohort curve comparison

`compare_curves.py COHORT_DIRECTORY METRIC_CURVES_JSON_GZ NEW_OUTPUT` compares a complete 50-seed summary with the pinned Figure 3–9 digitization.
It retains 3,876 records per pairing, including unresolved paper segments.
For each visible interval, it evaluates the piecewise-linear simulation mean over the horizontal calibration interval.
Signed separation is positive above the paper range, negative below, and zero when the ranges overlap.
These descriptive separations are not statistical acceptance tests; adjacent raster columns are dependent.
Paper seeds and between-run uncertainty remain unavailable.

The command records hashes of all consumed summary, mean, and digitization files.
Run `verify_cohort.R` on the same summary before interpreting the comparison.
Current validation covers two real-PDF extractions, pre-change endpoint execution, four complete-cohort comparisons, and exact preservation of 4,576 vision/metabolism comparison records. Use `results/horizontal-calibration-correction-2026-10-19/metric-curves.json.gz` with the current comparator.
The [complete Rule M/EC cohort](https://github.com/Metta-AI/sugarscape/tree/c320930a8fd0d670694dc4694e69687555f406b9/replications/brearcliffe_2020/results/rule-m-ec-complete-cohort-2026-10-19) now passes the full summary, independent R, and curve-comparison workflows. The Rule M/Rule M cohort now also passes those complete workflows.

[The additional 50 EC/EC inputs are durably preserved](https://github.com/Metta-AI/sugarscape/tree/c320930a8fd0d670694dc4694e69687555f406b9/replications/brearcliffe_2020/results/ec-ec-durable-evidence-2026-10-19): a fresh storage import verifies 502 file hashes. Both disjoint backups together cover all 303 audited inputs.

[Full-horizon EC/EC recorder qualification](https://github.com/Metta-AI/sugarscape/tree/c320930a8fd0d670694dc4694e69687555f406b9/replications/brearcliffe_2020/results/ec-ec-full-native-qualification-2026-10-19) matches native BehaviorSpace exactly on 320,016 values for seed 381016329. Fresh local readback passes; the paper discrepancy remains unresolved.

[Durable EC/Q evidence](https://github.com/Metta-AI/sugarscape/tree/c320930a8fd0d670694dc4694e69687555f406b9/replications/brearcliffe_2020/results/ec-q-durable-evidence-2026-10-19) passes fresh storage import and verification of 502 file hashes. The three disjoint backups now cover all 353 audited inputs.

[Durable EC/SARSA evidence](https://github.com/Metta-AI/sugarscape/tree/c320930a8fd0d670694dc4694e69687555f406b9/replications/brearcliffe_2020/results/ec-sarsa-durable-evidence-2026-10-19) verifies all 502 archive members after fresh storage download. Four disjoint backups now cover all 403 audited inputs.


## Final parameter comparison

[The reusable complete-cohort command](https://github.com/Metta-AI/sugarscape/tree/c320930a8fd0d670694dc4694e69687555f406b9/replications/brearcliffe_2020/results/parameter-comparison-cli-2026-10-20) defaults to all sixteen pairings and rejects missing evidence without writing a partial report. Its thirteen-pair execution reproduces all existing data fields and passes independent R verification. The [completed sixteen-pair execution](https://github.com/Metta-AI/sugarscape/tree/c320930a8fd0d670694dc4694e69687555f406b9/replications/brearcliffe_2020/results/sixteen-pair-parameter-comparison-2026-10-20) now passes independent R checks, with the final cohort-directory correction documented.

## Archived raw outputs

[The immutable experiment archive](https://github.com/Metta-AI/sugarscape/tree/b64684cbe24b2b17f5cb32819040db4581fe7e25/replications/brearcliffe_2020/results) retains raw runs and verbose diagnostics. They remain unchanged in existing local checkouts; summaries, source inputs, and analysis code stay tracked. Restore any required input with `git show b64684cbe24b2b17f5cb32819040db4581fe7e25:PATH > /absolute/output/path`, replacing `PATH` with its repository-relative path.

## Archived run records

Primary runners, analysis code, fixed study inputs, source provenance, and study findings remain tracked.
Dated run directories, checkpoint notes, copied runners, and generated source readbacks are preserved in [the experiment archive](https://github.com/Metta-AI/sugarscape/tree/c320930a8fd0d670694dc4694e69687555f406b9/replications/brearcliffe_2020).
Regenerated evidence belongs in the ignored output directories.

Commands and provenance records may reference archived inputs or historical scripts. Restore those dependencies before running the corresponding analysis:

```sh
git restore --source=c320930a8fd0d670694dc4694e69687555f406b9 --worktree -- REPOSITORY_PATH
```

Replace `REPOSITORY_PATH` with the required archived file or directory. The restore leaves the index unchanged and the restored evidence ignored. The [original evidence archive](https://github.com/Metta-AI/sugarscape/tree/7e88337b66d19ef04756679e72da74a7a05f6ec4/replications/brearcliffe_2020) retains raw outputs removed in previous cleanups.
