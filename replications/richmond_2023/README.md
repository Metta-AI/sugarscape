# Richmond et al. (2023): FLAME GPU 2 Sugarscape

Status: **incomplete; archived grid and aggregation audited, native replay unstarted**.
No completed-study credit. This study adds to the existing replication program.

Paper: [FLAME GPU 2: A framework for flexible and performant agent based simulation on GPUs](https://doi.org/10.1002/spe.3207).
Scope: the complete Sugarscape case study, Section 4.3 and Figures 6/11.
The paper's separate Boids experiments are outside this Sugarscape study.

## Pinned sources

The paper explicitly links the [benchmark v1 release](https://github.com/FLAMEGPU/FLAMEGPU2-submodel-benchmark/releases/tag/v1).
Its annotated tag object is `89eff8e11f28d20533b69b274be088f0a7045933`;
the peeled source commit is `290702073492677f2fc9164419e9d5900d119e02`.
The benchmark selects engine tag `v2.0.0-rc`, whose peeled commit is
`19136c18629af0a52ac4355ff705596b22bedac1`.
Keep the benchmark and engine in separate pinned checkouts; no simulation source
is copied or modified in this study directory.

The published release retains raw data, plotting scripts, figures, and machine notes.
Use `sample/data/v100-515.65.01/2.0.0-rc-v100-11.0-beltsoff` for Figure 11.
Older V100 and A100 directories represent different experiment versions.
The machine notes name a V100-SXM2-32GB, CUDA 11.0, and GCC 9.3.0, but list an
older driver than this data directory. Record that provenance difference explicitly.

## Archived numerical audit

[The audit](results/archive-2026-10-17/audit.json) checks every expected condition and
step, unique keys, finite timings, population bounds, and all native aggregate means:

| Experiment | Conditions | Per-condition observations |
| --- | ---: | ---: |
| Scaling, widths 256 through 4096 in increments of 256 | 48 | 100 steps |
| Occupation, six densities at width 512 | 18 | 100 steps |
| Conflict resolution, six densities at width 512 | 18 | Nine stored bins |

All 6,600 step records reconcile with 132 population/timing means.
The comparison bounds account for independent decimal rounding of each native CSV
value and aggregate; population observations are exact integers. No statistical
acceptance threshold or published effect criterion is inferred from these errors.
All 162 resolution rows have unique expected keys and valid bounds.
Raw inputs remain in the pinned author repository; their hashes are retained.

```sh
python replications/richmond_2023/audit_archive.py PINNED_BENCHMARK NEW_OUTPUT
```

This reproduces archived aggregation only. It does not rerun a simulation, verify
historical plot pixels, or establish a fresh performance result.

## Source discrepancies to preserve and investigate

- The README describes widths 64–4096 at increments of 64. The actual benchmark
  and selected data use 256–4096 at increments of 256.
- `MovementExitCondition` increments its counter before writing to
  `step_unresolved_count[counter]`. Index zero remains zero, but CSV labels start
  at one. Thus the first reported bin is an unused zero; the second records
  unresolved agents after the first resolution iteration.
- The counter writes only while its value is below nine. The ninth iteration
  is not measured before forced exit. Its successful conflict resolution cannot
  be inferred from the stored histogram alone.
- Resolution sums use unsigned integers and divide by three in place. Fractional
  mean unresolved counts are truncated before the plotting script divides by
  mean population. The archived audit does not recover the omitted fractions.
- Source maxima are metabolism four and sugar capacity four. The paper's prose
  lists metabolism five and gives inconsistent sugar maxima. Preserve source
  behavior in the native replay; label any alternative configuration separately.

These findings identify measurement and specification questions. They are not a
negative paper verdict. Fresh state observations must establish collision freedom,
resolution completion, and the consequences of these differences.

## Required native replication

Run the complete original 84-condition experiment: seeds 0–2; 48 scaling and
18 occupation conditions at 100 steps; 18 resolution conditions at three steps.
Freeze engine/source hashes, compiler/CUDA versions, GPU identity, clocks, build
flags, runtime environment, and raw outputs. Preserve original seatbelts-off
benchmark timing; run additional instrumented state checks separately.

Recompute Figure 11A population means, Figure 11B resolution summaries, and
Figure 11C scaling from all native records. Retain original and corrected bin
interpretations separately. Reconstruct the three visualisation states for
Figure 11D–F and audit the movement dependency graph against Figure 6.

Before performance interpretation, specify hardware comparisons and seed-level
uncertainty. Historical absolute seconds are not portable acceptance criteria.
No GPU allocation or native run has started. A bounded toolchain and full-workflow
qualification must precede the complete benchmark; shortened runs receive no
full-study credit. Existing study ensembles remain unchanged.
