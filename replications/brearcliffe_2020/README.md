# Brearcliffe and Crooks: Creating Intelligent Agents

[EC/Rule M now completes all 50 seeds](results/ec-rule-m-complete-cohort-2026-10-19), with full-trajectory audit and independent R verification. Five of sixteen released-code pairings have complete cohorts. Total audited coverage is 250 released-code plus three paper-table inputs, totaling 5,060,253 observations. Thirteen of fourteen EC/Rule M endpoint ranges overlap the paper raster intervals. The remaining EC vision comparison has a narrowly overlapping bootstrap interval; no whole-paper verdict is established.

Figure 6's Rule M/Q-learning cell contains an “M v M” chart nearly identical to the Rule M/Rule M panel. Both curves are excluded from agreement judgments. Eleven of twelve remaining endpoint range comparisons overlap the paper raster intervals; this is not equivalence or a negative replication.

[The 112-panel title and placement audit](results/figure-title-audit-2026-10-19) confirms the two known Figure 6 conflicts and finds no additional title conflict. OCR mismatches were checked against enlarged source images; all inventory rectangles match the PDF. This does not validate the underlying curve data.

[Both cloud-host qualification cases now pass](results/existing-host-qualified-ensemble-launch-2026-10-19): 640,032 values and both complete trajectory byte sequences match the local references. The 749 reserved released-code inputs are running with eight workers under an 11.5-hour simulation bound and a $9.12 execution/export/idle ceiling. Launch adds no completed-study credit.

[Both paper-table pilot inputs](results/second-paper-table-input-2026-10-19) pass all 20,001 observation checks and fresh archive readback. These two paper-table inputs are included in the current audited total above; Rule M/EC and Rule M/Rule M are complete; the other pairings remain incomplete.

[The earlier released-code prefix](results/rule-m-prefix-2026-10-19) retains its 15-input audit snapshot; the current totals above supersede that snapshot.

[The first two paper-table Q-Learning/SARSA inputs](results/paper-table-rl-launch-2026-10-19) completed sequentially within the 2,100-second batch limit. Both outputs are now independently audited.

[Corrected Figure 3–9 horizontal calibration](results/horizontal-calibration-correction-2026-10-19) uses each figure’s actual plot boundary, verified across all 112 panels. It supersedes the earlier full-curve digitization and four cohort comparisons. Shared early combat/starvation deviations disappear; the EC vision discrepancy remains. All retained vertical measurements and simulation summaries are unchanged.

[Figures 4–9 endpoint targets](results/metric-digitization-2026-10-19) now retain 170 visible raster bounds and 22 unresolved endpoints across six metrics. Repeated extraction is byte-identical; these image bounds are not statistical confidence intervals.

[The EC vision uncertainty diagnostic](results/ec-vision-uncertainty-2026-10-19) finds all 286 paper raster intervals overlap an exploratory whole-run bootstrap band. Independent R confirms native-input interpolation and resampling arithmetic. This makes sampling uncertainty a plausible explanation, not an equivalence result.

[A full native paper-table Rule M/Rule M control](results/paper-table-rule-m-control-2026-10-19) matches its released-code counterpart byte-for-byte across 20,001 observations. This supports the source audit’s predicted parameter insensitivity for that input; unexecuted inputs receive no credit.

[Durable evidence for all 253 currently audited inputs](results/durable-evidence-2026-10-19) is uploaded and independently read back from storage: seven archives and 2,569 files match their hashes. This preserves existing results without adding coverage.

Study status: native recorder corrected and qualified across 20,000 ticks. No reproduced-paper result yet.

Paper: [Creating Intelligent Agents: Combining Agent-Based Modeling with Machine Learning](https://doi.org/10.1007/978-3-030-83418-0_3).
The [author-deposited release](https://www.comses.net/codebases/ffb52fc3-69e1-4bbd-b5d7-fa460617f74e/releases/1.0.0/) includes the NetLogo model, symmetric map, and ODD description.
`source-audit.json` pins the downloaded artifacts and author manuscript. Preserve their original license notices.
The model header states CC-BY-NC-SA 3.0; release metadata states 4.0. This study does not relabel or relicense those sources.

The paper compares 16 ordered method pairings, 50 runs each, through ticks 0–20,000.
Seven per-breed statistics feed Figures 3–9. The original population slider is 400 per breed, yielding 800 initial agents.
The released experiment specifies only five repetitions and calls `random-seed new-seed`; it does not record historical seeds.
The manuscript states learning rate 0.8 and discount rate 0.9; the source sets learning rate 0.9 and gamma 0.8.
Keep the released-code interpretation separate from a prose-parameter sensitivity experiment; neither resolves historical settings by itself.
[The pinned dependency audit](results/parameter-dependencies-2026-10-19) identifies twelve parameter-sensitive pairings and four pairings using only Rule M/EC. All 800 paired models retain identical seeds and differ only in the two literals. Coverage remains unchanged; source-level sharing is not credited as executed inputs.

## Recover source inputs

The [tested source-recovery CLI](results/source-recovery-2026-10-19) retrieves the exact author artifacts and verifies every archive member, including license and citation notices.
Use new output directories; mismatched downloads fail visibly and remain available for inspection.

```sh
python replications/brearcliffe_2020/fetch_sources.py /new/source-directory
python replications/brearcliffe_2020/prepare_ensemble.py \
  /new/source-directory/release/code/Creating_Intelligent_Agents.nlogo /new/prepared-directory
```

The resulting 1,602 files match the frozen preparation used by this study.
These commands prepare inputs only. Execution still requires the qualified NetLogo 6.1.1 runtime, matrix extension, and recorder described below.

## Native pilot

The [launch record](results/native-pilot-launch-2026-10-19) selects Rule M versus evolutionary computing, with combat, corner starts, replacement, and growback 1.
This pairing does not use the disputed reinforcement-learning hyperparameters.
A separate retained model copy replaces only `random-seed new-seed` with `random-seed 20261019`.
The original source remains unchanged. This fixed seed is prospective, not a recovered author seed.

`Replay.java` uses NetLogo 6.1.1 and its original bundled matrix extension.
It records initial state and every subsequent tick, with both populations and all fourteen figure statistics.
A complete run must contain 20,001 finite observations with consecutive tick values.
The pilot has a 600-second wall limit, 1 GiB Java heap, and 50 MiB output cap. Partial outputs remain evidence, without completion credit.
The first full pilot completed but failed recorder qualification. The [retained discrepancy and correction](results/recorder-qualification-2026-10-19) show exact short-run agreement after isolating measurement randomness. The [full-horizon comparison](results/full-recorder-qualification-2026-10-19) now agrees exactly on all 320,016 values across 20,001 observations.

Compile against the NetLogo application JARs, then run:

```sh
java -Xmx1g -Djava.awt.headless=true -cp 'DRIVER_DIRECTORY:NETLOGO/app/*' \
  Replay /absolute/seeded-model.nlogo 'Rule M' EC 20000 /new/trajectory.csv
```

Place the original symmetric map and the NetLogo 6.1.1 matrix extension beside the retained model copy.
The external bounded launcher and exact command are retained in the launch record.

The [all-pairing qualification](results/all-pairings-qualified-2026-10-19) now passes: all 256,256 values match native BehaviorSpace through 1,000 ticks for all sixteen pairings. The [first frozen Rule M/EC input](results/first-ensemble-input-complete-2026-10-19) completes and passes fresh archive audit; complete ensembles remain outstanding.

The [full learning-method comparison](results/rl-full-qualified-2026-10-19) passes: all 320,016 values match native BehaviorSpace through 20,000 ticks for Q-Learning versus SARSA.
The [frozen ensemble preparation](results/ensemble-preparation-2026-10-19) defines 800 runs for each parameter interpretation, with matched prospective seeds. Both preparations reproduce identical bytes; one released-code input has completed and passed independent audit.

The [Figure 3 digitization](results/wealth-digitization-2026-10-19) recovers 30 visible endpoint intervals and leaves two occluded endpoints unresolved. Four last-row panel labels were corrected after checking plot titles; rejected labels remain documented.

A [bounded CPU host trial](results/cloud-qualification-launch-2026-10-19) is queued to verify two complete trajectories before scaling the frozen ensembles.

The [first bounded dispatcher batch](results/first-batch-complete-2026-10-19) completes both inputs and passes fresh archive audit. Released-code coverage is 3/800 inputs, including the earlier Rule M/EC input.

The [original local Rule M/Rule M batch](results/rule-m-cohort-launch-2026-10-19) has ended. Its 40 successes and the two earlier controls give 42 complete seeds; the eight unfinished inputs are recovering remotely.

The [cohort analysis](results/cohort-analysis-preparation-2026-10-19) is specified and rejects incomplete samples before producing means. [An independent R checker](results/cohort-verification-preparation-2026-10-19) is prepared for all means, standard deviations, and bootstrap intervals. The complete Rule M/EC and Rule M/Rule M cohorts now pass the fifty-run summary, independent arithmetic check, and numerical comparison.

## Remaining work

Qualify the remaining method pairings and estimate their runtime before the full 800-run ensemble. The measured Rule M/EC pairing projects to about 49 CPU-hours for 800 runs; this is not a measured full-sweep estimate.
Resolve the released-code/prose parameter interpretations without silently changing the primary experiment.
Implement the study behavior in the fork, qualify it against the native model, and compare every published figure using full repeated ensembles.
Do not count a pilot, source audit, or five-repeat released sweep as a completed paper replication.

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
The [complete Rule M/EC cohort](results/rule-m-ec-complete-cohort-2026-10-19) now passes the full summary, independent R, and curve-comparison workflows. The Rule M/Rule M cohort now also passes those complete workflows.
