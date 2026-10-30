# The Need for Greed in Artificial Decisionmakers

**Incomplete native reproduction.** Audited coverage is 1,205 unique inputs and 5,005,871 observations: all 400 baselines and 805 sweep inputs. Another 9,295 sweep inputs remain.

Tables I–III reproduce their published counts. The complete Table IV row at selfishness 0.36–0.40 reproduces 1.2% extinct, 0% worse, and 98.8% better across 500 original inputs, with independent R checks. Incomplete rows receive no percentage estimates.

Four measurements agree graphically at selfishness 0.36 and 0.37. Death-rate definitions, historical aggregation, remaining sweep inputs, and complete figure comparisons remain unresolved.

Kremer-Herman and Gupta, IEEE ISTAS 2024, pages 182–190. [Author manuscript](https://digital-terraria-lab.github.io/assets/papers/kremer-herman:2024:need-for-greed.pdf).
The paper explicitly names [author release v2024.1](https://github.com/digital-terraria-lab/sugarscape/tree/b9ca671ab7591c7b3606f2d76c33eda344d626d1). Its source is MIT-licensed; source and dataset hashes appear in `source-audit.json`.

The deposited protocol includes 400 baseline inputs and 10,100 sweep inputs: 101 selfishness levels, 100 original seeds each, and 5,000 steps. These configurations are byte-identical subsets of the Blueprints datasets. Reuse requires matching configurations, source manifests, and raw trajectories; matching names alone is insufficient.

## Audited evidence

- [Baseline reuse](https://github.com/Metta-AI/sugarscape/tree/af827ca035bd40cddd43d68209221381cac3102a/replications/need_for_greed_2024/results/baseline-reuse-2026-10-19): 64 Bentham baseline inputs, 320,064 observations. Three endpoint controls and 240 recovered inputs extend baseline coverage to 307; 93 remain.
- [Selfishness 0.37](https://github.com/Metta-AI/sugarscape/tree/af827ca035bd40cddd43d68209221381cac3102a/replications/need_for_greed_2024/results/selfishness037-reuse-2026-10-19): all 100 deposited seeds, 495,265 observations, one extinction and 99 populations above the initial 250. No final population equals the initial population. Three endpoint controls and 227 Table IV batch inputs extend sweep coverage to 330; 9,770 remain.

Baseline and sweep configurations remain separate. Baseline selfishness endpoints are not substituted for sweep endpoints. Reused PyPy trajectories inherit the Blueprints runtime qualifications; this audit adds configuration and artifact verification, not an independent engine implementation.

The 0.37 cohort’s median per-run population mean is 1,151.480303939 including the initial row, or 1,151.6606 excluding it. Zero extension after extinction leaves both medians unchanged. [Direct Figure 2 vector extraction](https://github.com/Metta-AI/sugarscape/tree/af827ca035bd40cddd43d68209221381cac3102a/replications/need_for_greed_2024/results/figure2-population-2026-10-19) places both medians within the plotted stroke at selfishness 0.37. All four averaging conventions agree graphically; historical averaging remains unresolved.

Table IV combines levels 0.36–0.40, requiring 500 inputs. This single level does not reproduce that row. The paper classifies equality with the initial population as worse; the released plot classifies equality as better. Both remain distinguishable in retained endpoint counts.

## Repeat the fresh artifact audit

The verifier consumes the retained Need for Greed ZIP and Blueprints study artifacts. These are explicitly recorded dependencies, not downloaded or generated silently.

```sh
python replications/need_for_greed_2024/results/selfishness037-reuse-2026-10-19/verify.py /path/to/workspace /new/audit.json
```

The workspace must contain `sugarscape-blueprints` at its recorded evidence paths and `sugarscape-replication-evidence/papers/need-for-greed.zip`. The output must not exist. Every source archive, manifest, configuration and raw trajectory is checked before producing the report. The two full readbacks match byte-for-byte; independent NumPy arithmetic checks four medians and endpoint counts.

The first auditor attempt compared a nested hash mapping with its enclosing document. It failed before reporting results. The corrected schema access, original script, and failure receipt are preserved; no simulation was rerun or excluded.

[Native endpoint controls](https://github.com/Metta-AI/sugarscape/tree/af827ca035bd40cddd43d68209221381cac3102a/replications/need_for_greed_2024/results/endpoint-qualification-launch-2026-10-19) now test whether baseline configurations reproduce sweep endpoints. The selected selfishness-zero pair matches all 137 observations byte-for-byte through extinction. [The complete 0.5 pair](https://github.com/Metta-AI/sugarscape/tree/af827ca035bd40cddd43d68209221381cac3102a/replications/need_for_greed_2024/results/midpoint-control-2026-10-19) also matches byte-for-byte across 5,001 observations, and reproduces its prior baseline hash. [The complete 1.0 pair and six-input reconciliation](https://github.com/Metta-AI/sugarscape/tree/af827ca035bd40cddd43d68209221381cac3102a/replications/need_for_greed_2024/results/endpoint-controls-complete-2026-10-19) now verify all 5,001 level-1 observations and add six disjoint original inputs.

[All five measurements at selfishness 0.37](https://github.com/Metta-AI/sugarscape/tree/af827ca035bd40cddd43d68209221381cac3102a/replications/need_for_greed_2024/results/all-metric-comparison-2026-10-19) now have raw-trajectory arithmetic checks. Four medians agree graphically. Starvation-plus-combat death rates do not; adding aging deaths gives graphical agreement but contradicts the written metric. This remains a measurement investigation, not a validated negative replication.

[The later author plotting control](https://github.com/Metta-AI/sugarscape/tree/af827ca035bd40cddd43d68209221381cac3102a/replications/need_for_greed_2024/results/later-author-death-control-2026-10-19) also gives graphical agreement for death rates when aging is included. Its 5,001 rates pass independent arithmetic checks, but neither its later source version nor its pooled aggregation establishes the paper’s historical pipeline.

[The original-input inventory](https://github.com/Metta-AI/sugarscape/tree/af827ca035bd40cddd43d68209221381cac3102a/replications/need_for_greed_2024/results/remaining-input-plan-2026-10-19) separates 164 audited inputs, six reserved controls, and 10,330 remaining inputs. Recover the remaining baseline evidence before rerunning it. The single-condition compute projection is about $134 before overhead; the separately bounded Table IV batch above is now submitted.

## Execute an original input

The [qualified native runner](https://github.com/Metta-AI/sugarscape/tree/af827ca035bd40cddd43d68209221381cac3102a/replications/need_for_greed_2024/results/native-runner-qualified-2026-10-19) accepts either an original baseline or sweep configuration. It requires Python with Pydantic and GNU `timeout`.

```sh
python replications/need_for_greed_2024/run_native.py AUTHOR_ENGINE NEED_FOR_GREED_ZIP ORIGINAL_ENTRY NEW_OUTPUT --seconds 900
python replications/need_for_greed_2024/verify_runner.py WORKSPACE NEW_VERIFICATION_OUTPUT
```

Both commands require the pinned author artifacts documented above. Each run preserves source, configuration, runtime, command, timeout, and trajectory evidence. A zero native exit is followed by full trajectory validation before any success result is written. Failed or timed-out runs remain evidence and receive no success result.

## Remaining work

All baseline trajectories are verified. Execute or reuse the remaining sweep inputs to cover the declared method and parameter range. Complete the Table IV and Figures 2–6 comparisons with declared aggregation and denominator conventions. Numerical agreement is not required for method-reproduction completion; unresolved implementation choices still require investigation. Investigate discrepancies against the released code and original protocol before assigning a negative replication result.

Historical boxplot aggregation remains unresolved. The paper’s printed Table IV row 0.81–0.85 sums to 100.2%; the source audit preserves it without correction. Full paper completion requires the complete declared experiment and qualified comparisons, not this subset.

## Archived raw outputs

[The immutable experiment archive](https://github.com/Metta-AI/sugarscape/tree/32d24ff439a3f5ee74e6650b880bfb2187a5ea7f/replications/need_for_greed_2024/results) retains raw runs and verbose diagnostics. They remain unchanged in existing local checkouts; summaries, source inputs, and analysis code stay tracked. Restore any required input with `git show 32d24ff439a3f5ee74e6650b880bfb2187a5ea7f:PATH > /absolute/output/path`, replacing `PATH` with its repository-relative path.

## Archived run records

Primary runners, analysis code, fixed study inputs, source provenance, and study findings remain tracked.
Dated run directories, checkpoint notes, copied runners, and generated source readbacks are preserved in [the experiment archive](https://github.com/Metta-AI/sugarscape/tree/af827ca035bd40cddd43d68209221381cac3102a/replications/need_for_greed_2024).
Regenerated evidence belongs in the ignored output directories.

Commands and provenance records may reference archived inputs or historical scripts. Restore those dependencies before running the corresponding analysis:

```sh
git restore --source=af827ca035bd40cddd43d68209221381cac3102a --worktree -- REPOSITORY_PATH
```

Replace `REPOSITORY_PATH` with the required archived file or directory. The restore leaves the index unchanged and the restored evidence ignored. The [original evidence archive](https://github.com/Metta-AI/sugarscape/tree/124fb920ce78f6a2ea6721a4db797c6dc9111b22/replications/need_for_greed_2024) retains raw outputs removed in previous cleanups.
