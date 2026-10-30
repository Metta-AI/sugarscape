# Thaler and Siebers (2019): parallel Sugarscape

Status: **completed qualified author-code method reproduction** under the user’s October 19 criterion. [Evidence and qualifications](https://github.com/Metta-AI/sugarscape/tree/0b7543e418d3a0c4e053394a350a0031d2cd7661/replications/thaler_2019/results/method-verdict-2026-10-19) separate complete execution from historical numerical agreement. Figure 5a requires time 83 rather than caption time 50; timing and retry discrepancies remain explicit.

Paper: [A tale of lock-free agents](https://doi.org/10.1186/s40294-019-0067-9),
Complex Adaptive Systems Modeling 7, 5, published December 26, 2019.
[Original implementation](https://github.com/thalerjonathan/haskell-stm-sugarscape)
uses BSD3 licenses in each project. The paper is CC BY 4.0.

## Scope and outstanding work

Reproduce the paper's Sugarscape case study: Figure 5 population dynamics;
Tables 6–9 and Figures 6–7 covering timing, scaling, and transaction retries.
The separate SIR epidemic case study is outside this Sugarscape study.

The native model uses a 50×50 toroidal landscape, initial population 500,
endowment 5–25, metabolism 1–5, vision 1–6, and growback one per step.
Agents die from starvation, without ageing. Sequential execution shuffles agents;
concurrent execution delegates ordering to the scheduler. The sequential implementation
shuffles the environment behavior together with agents. Concurrent implementations
run growback synchronously after the population. Performance runs use 1,000 steps and seed 42.
The scaling experiment replaces dead agents and varies initial population from
500 to 2,500 in increments of 500. Preserve the released landscape and random initialization.

Completed execution and remaining interpretation:

- Figure 5b reproduces all 50 original values. Figure 5a matches all occupied cells at exported time 83, while its caption names time 50.
- All 51 timing cells across Tables 6, 8 and 9 pass native audit, covering 204 raw measurements.
- The Table 7 retry ensemble and Table 9 retry runs are complete. The 32-capability normal retry discrepancy remains unexplained.
- Concurrent population and observer checks remain in the archive; no rigorous statistical dynamics-equivalence result is claimed.
- [The timing proposition audit](https://github.com/Metta-AI/sugarscape/tree/0b7543e418d3a0c4e053394a350a0031d2cd7661/replications/thaler_2019/results/timing-proposition-audit-2026-10-19) separates three internal reporting inconsistencies from fresh performance differences.

The paper's local machine was an i7-8550U laptop, Ubuntu 19.10, with GHC 8.4.3
and Stack resolver lts-12.4. Tables 6/8 use different hardware in our runs.
Table 9 matches instance class, but historical clock and scheduling conditions remain unknown.
The fixed execution protocols and source checks support descriptive comparisons.
No numerical equivalence threshold or post-hoc significance criterion is introduced.
Historical performance interpretation and retry-discrepancy resolution remain open numerical-provenance questions. They do not prevent the qualified method verdict above; earlier dated verdicts remain unchanged.

## Source fidelity

Use timing revision `f5851488bf2369e2bbdc3f2499ed69c142de9fec`.
All 61 model/build files match revision `b6c4aeccdc153f26edef9709764e055e4e36b806`,
which contains the completed local experiments.

Revision `6a79b8b2e623c288c087b91aff400ac2c4d95510` enables TArray retry instrumentation.
Its source explicitly warns of reduced performance. It is suitable for toolchain
validation and instrumented measurements, not the uninstrumented timing comparison.
Latest revision `2bf138a8b5f1d020f09781932e110091802f6dcc` additionally replaces the
sequential benchmark entry point with population CSV export.
[Revision hashes](https://github.com/Metta-AI/sugarscape/blob/0f0c4350672e75a47a8373c119b7291a8d0c2168/replications/thaler_2019/results/archived/revision-fidelity.json) retain these distinctions.

The pinned `stm-stats-0.2.0.0` library computes retries divided by commits,
not retries divided by attempts. Its counters persist within the process;
record process boundaries and cumulative counts when interpreting repeated benchmarks.

## Reproduced archived analysis

The audit reads 53 complete author Criterion HTML reports, checks their SHA-256
hashes, and independently fits ordinary least squares to 212 raw measurements.
All regression slopes match within 1.99e-13 seconds. All 51 printed timing cells
in Tables 6, 8 and 9 match after rounding to three significant digits.
All 53 archived sample standard deviations also reproduce from the raw per-iteration timings.
Of 45 printed standard deviations, 30 match rounding to the nearest hundredth; 15 differ.
The largest absolute difference is 0.008984 seconds. These reporting differences remain explicit;
no alternative tolerance or negative paper verdict is assigned. Table 9 parentheses are retry ratios,
which cannot be reconstructed from these timing samples and remain unvalidated.

These are author archival measurements, not fresh simulation runs, independent
engine validation, or a hardware performance replication. The separate archived native
execution proof verifies full original-model runs, without a timing verdict.

From this checkout, with Python 3.11, NumPy 1.26.4 and Poppler `pdftotext` installed:

```bash
python replications/thaler_2019/audit_archive.py \
  /path/to/haskell-stm-sugarscape \
  /path/to/s40294-019-0067-9.pdf \
  /path/to/new-audit-directory
```

The author checkout must contain the pinned report files, available at latest
revision above. Download the publisher PDF from
`https://link.springer.com/content/pdf/10.1186/s40294-019-0067-9.pdf`.
The command requires a new output directory and rejects changed paper/report bytes.
Archived results retain individual raw-report paths, recomputed slopes, paper
cells, and limitations. Full raw HTML remains in the pinned original repository.

## Completed native checks and interpretation

[The complete timing grid](https://github.com/Metta-AI/sugarscape/tree/0f0c4350672e75a47a8373c119b7291a8d0c2168/replications/thaler_2019/results/timing-grid-complete-2026-10-18) covers 25 Table 6, 20 Table 8, and six Table 9 conditions.
All 204 raw measurements pass native audits. Table 8 preserves 28/30 pairwise orderings of fitted means versus printed times.
Native/published timing ratios span 0.1728–0.6115, 0.2921–0.6150, and 1.0711–1.4165 respectively.
Hardware and historical scheduling differences prevent a timing-equivalence verdict.

[The Figure 5a source control](https://github.com/Metta-AI/sugarscape/tree/0b7543e418d3a0c4e053394a350a0031d2cd7661/replications/thaler_2019/results/figure-source-resolution-2026-10-18) matches all 201 occupied cells at time 83, while the caption names time 50.
It also separates all 2,299 visible unoccupied cells by native sugar level and reproduces all 50 Figure 5b values.

[The completed retry diagnostic](https://github.com/Metta-AI/sugarscape/tree/0b7543e418d3a0c4e053394a350a0031d2cd7661/replications/thaler_2019/results/criterion-retry-control-complete-2026-10-18) audits 51 simulations across six processes.
Default Criterion gives mean retry ratio 0.0871433; fresh single processes give 0.0894201, versus published 0.29.
Repetition does not explain the discrepancy in this control. Historical scheduling equivalence remains unresolved.

[Four original TArray runs](https://github.com/Metta-AI/sugarscape/tree/0b7543e418d3a0c4e053394a350a0031d2cd7661/replications/thaler_2019/results/population-semantics-complete-2026-10-19) validate 4,000 observations.
Both rebirth runs retain exactly 2,500 occupied cells, despite ending with 2,320 returned agent observations.
This resolves the apparent population deficit as a measurement-interpretation issue, while timing and retry qualifications remain.

## Archived run records

Primary runners, analysis code, fixed study inputs, source provenance, and study findings remain tracked.
Dated run directories, checkpoint notes, copied runners, and generated source readbacks are preserved in [the experiment archive](https://github.com/Metta-AI/sugarscape/tree/0b7543e418d3a0c4e053394a350a0031d2cd7661/replications/thaler_2019).
Regenerated evidence belongs in the ignored output directories.

Commands and provenance records may reference archived inputs or historical scripts. Restore those dependencies before running the corresponding analysis:

```sh
git restore --source=0b7543e418d3a0c4e053394a350a0031d2cd7661 --worktree -- REPOSITORY_PATH
```

Replace `REPOSITORY_PATH` with the required archived file or directory. The restore leaves the index unchanged and the restored evidence ignored. The [original evidence archive](https://github.com/Metta-AI/sugarscape/tree/0f0c4350672e75a47a8373c119b7291a8d0c2168/replications/thaler_2019) retains raw outputs removed in previous cleanups.
