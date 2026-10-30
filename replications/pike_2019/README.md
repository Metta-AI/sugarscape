# Multi-Level Mesa (Pike, 2019)

[The common-resource history audit](https://github.com/Metta-AI/sugarscape/tree/9dfc564280813da402cf3442222d77f581b1360f/replications/pike_2019/results/common-source-history-2026-10-20) checks all eight ancestors of the selected pre-publication revision. Four policy/agent files are byte-identical in all 32 snapshots. Their pooling defect cannot be attributed to an edit within that history; historical installed dependencies and working-tree provenance remain unknown. Numerical validity still fails, and the study remains incomplete.

Status: **incomplete study**. All declared native experiment grids and the controlled timing ensemble have completed their audits. Numerical validity, historical source fidelity, and several published interpretations remain unresolved.

## Current claim coverage

Later complete analyses supersede the launch and prefix records retained below.

| Paper target | Current evidence | Unresolved requirement |
| --- | --- | --- |
| Phase I survival and prices | [300 runs](https://github.com/Metta-AI/sugarscape/blob/bd7858f34b6f9fb7b4abc4f8b68884eb17149f31/replications/pike_2019/results/phase1-analysis-2026-10-17/analysis.json); native notebook histograms independently reconstructed | Historical survivor means differ; original seeds and equivalence margin unavailable |
| Phase II trade thresholds | [600 runs](https://github.com/Metta-AI/sugarscape/blob/bd7858f34b6f9fb7b4abc4f8b68884eb17149f31/replications/pike_2019/results/phase2-analysis-2026-10-17/analysis.json), thresholds 1/5/10 | Similar means and intervals spanning zero do not prove the reported equivalence |
| Movement policies | [1,200 runs](https://github.com/Metta-AI/sugarscape/blob/bd7858f34b6f9fb7b4abc4f8b68884eb17149f31/replications/pike_2019/results/phase3-analysis-2026-10-17/movement/analysis.json), including separately labeled selector corrections | Released selector disagrees with the stated rule; corrections do not establish historical behavior |
| Price-direction claims | [2,100-run analysis](https://github.com/Metta-AI/sugarscape/blob/bd7858f34b6f9fb7b4abc4f8b68884eb17149f31/replications/pike_2019/results/convergence-2026-10-17/analysis.json) supports finite-horizon directions | Retrospective windows do not establish asymptotic convergence or recover the plotted historical trajectories |
| Common-resource thresholds | [400 conditions](https://github.com/Metta-AI/sugarscape/blob/bd7858f34b6f9fb7b4abc4f8b68884eb17149f31/replications/pike_2019/results/common-threshold-complete-2026-10-17/comparison.json), all seeds at thresholds 5/10 | Every condition contains nonfinite holdings; the approximately 400-higher central-peak claim lacks a precise comparison target |
| Runtime comparisons | [900 controlled runs](https://github.com/Metta-AI/sugarscape/tree/9dfc564280813da402cf3442222d77f581b1360f/replications/pike_2019/results/timing-complete-2026-10-17), native and full-step timers | Native timing excludes network reassessment; common-resource timings accompany invalid economic trajectories |

Historical source identification remains shared across these targets. The released
shared-resource code double-counts stale contributions in a passive, byte-identical
trace. Separately labeled conservation and lifecycle corrections change model rules;
they cannot be substituted for a faithful historical replay. The completed grids
therefore do not establish either a positive or validated negative whole-paper result.

Direct inspection of Figure 3-9 (PDF page 26) shows only the threshold-ten comparison.
It supplies no threshold-five histogram from which to recover the prose's central-peak
increase. The largest bin in our histograms is not substituted for that unspecified
central peak. This is a target-definition limitation, not an omitted ensemble.


The [paper](https://arxiv.org/abs/1904.08315) links the author's [Sugarscape](https://github.com/tpike3/SugarScape) and [Multi-Level Mesa](https://github.com/tpike3/multilevel_mesa) implementations.
We select their last pre-publication revisions, respectively `585e53398f4f58e89ec184c83bb20819f0e4c96a` and `99d2091721076df9fff32e8b49a0e33e98c34a6f`.
Chronology does not prove these are the exact paper versions. Both repositories have MIT licenses; simulation sources remain in separate unchanged checkouts.

## Execution and measurements

`run.py ENGINE LIBRARY standard|explicit|network NUMPY_SEED NEW_OUTPUT` runs 1,000 steps with the released 200-agent, 50×50 configuration and Mesa seed 42.
Use Mesa 0.8.5. Historical library requirements specify Mesa >=0.8.5 and NetworkX >=2.2.
Our initial runtime uses Python 3.11.14, NumPy 1.26.4 and NetworkX 3.6.1; it is not claimed to match the historical environment.
Mesa 0.8.4 lacks the required model random generator. Mesa 0.8.8 changes grid containers, breaking the original empty-cell comparison.
The author's 2021 fix is not applied to these historical runs.

The released runners fix Mesa seed 42 but leave NumPy unseeded. Our explicit NumPy seed makes replication possible; original NumPy states are unavailable.
The runner retains source hashes, initial agents, native price records, native model reporters, individual identities and health records.
It reads agent registries after each native step without drawing random numbers or modifying the model.
The network variant's native `survivors` reporter counts scheduled groups/resources, so it must not be interpreted as individual population.
Individual counts instead use `ml.agents_by_type[NetAgent]` and reconcile with native health records.

`audit_observation.py NATIVE OBSERVED NEW_OUTPUT` requires byte-identical native price and reporter outputs, then checks every surviving identity against health records.
Initial standard and explicit pilots each finish with 47 individual agents. Each is one run, not an ensemble estimate.
The standard pilot repeats byte-identically in a separate process. Observer validation covers 1,000 steps and 51,622 standard or 51,642 explicit health records.

## Targets and full scope

[Extracted notebook targets](notebook_targets.json) retain source cells, cached outputs and notebook hashes.
Five original multi-level common-resource data files are retained in the author's repository and audited below.
The earlier claim that all original raw datasets were omitted was incorrect.
Other experiment datasets remain unrecovered; cached outputs are reference evidence, not regenerated results.
Phase I cached mean survivors are standard 46.18, explicit 46.96 and network 46.68.
Common-resource cached means are one-level 94.35 and multi-level 92.83, matching the paper.
The notebooks multiply SciPy's already two-sided `ttest_ind` p-values by two, including a reported value above one.
Report the original analysis and correctly computed p-values separately; nonsignificance alone does not establish equivalence.

The full study scope covers the paper's Sugarscape experiments:

- Phase I: three approaches, 100 runs of 1,000 steps each; price convergence, dispersion, trade volume and survivor distributions.
- Phase II: explicit/network groups at thresholds of one, five and ten trades, with 100 runs per configuration.
- Phase III: group movement policies and one-level/multi-level common resources, including threshold comparisons and survival effects.
- Audit price aggregation against the original notebooks and preserve failed runs and undefined statistics.
- Quantify seed uncertainty; identify historical configuration differences before any negative verdict.
- Assess runtime comparisons on a controlled machine; historical wall-clock seconds are not portable targets.

Native ranges also need explicit accounting: `randint(1,6)` and `randrange(25,50)` exclude their upper endpoints, whereas the paper describes inclusive-looking ranges.
No rules or ranges are silently changed to match the prose. This PR establishes the runnable reference study inside the Metta-AI fork; independent model integration and full replication remain outstanding.

[Retained pilot evidence](https://github.com/Metta-AI/sugarscape/tree/bd7858f34b6f9fb7b4abc4f8b68884eb17149f31/replications/pike_2019/results/pilots-2026-10-16) now includes all three observer audits and compressed raw records.
The network pilot has 47 individual survivors but a native reporter value of 2,544 at termination.
All three observer replays match their native price and reporter outputs byte-for-byte, covering 3,000 steps and 154,898 health records.
Notebook source excerpts are distributed under the [author's MIT license](AUTHOR_LICENSE).

## Preserved evidence

[The full experiment record](https://github.com/Metta-AI/sugarscape/blob/2e438a8a0b928a2686d0caabd315c15c911b5498/replications/pike_2019/README.md) retains dated runs, budgets, failures, source hashes, figures, and detailed controls. Existing histories, outputs, and checkpoints remain unchanged. Historical launch notes do not establish current job status. Restore archived raw inputs before rerunning an analysis, as described in that record.

## Archived run records

Primary runners, analysis code, fixed study inputs, source provenance, and study findings remain tracked.
Dated run directories, checkpoint notes, copied runners, and generated source readbacks are preserved in [the experiment archive](https://github.com/Metta-AI/sugarscape/tree/9dfc564280813da402cf3442222d77f581b1360f/replications/pike_2019).
Regenerated evidence belongs in the ignored output directories.

Commands and provenance records may reference archived inputs or historical scripts. Restore those dependencies before running the corresponding analysis:

```sh
git restore --source=9dfc564280813da402cf3442222d77f581b1360f --worktree -- REPOSITORY_PATH
```

Replace `REPOSITORY_PATH` with the required archived file or directory. The restore leaves the index unchanged and the restored evidence ignored. The [original evidence archive](https://github.com/Metta-AI/sugarscape/tree/bd7858f34b6f9fb7b4abc4f8b68884eb17149f31/replications/pike_2019) retains raw outputs removed in previous cleanups.
