# Thaler and Siebers (2019): parallel Sugarscape

Status: **partial, archived-analysis reproduction only**. No completion credit.

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
concurrent execution delegates ordering to the scheduler. Growback runs synchronously
following the population. Performance runs use 1,000 steps and seed 42.
The scaling experiment replaces dead agents and varies initial population from
500 to 2,500 in increments of 500. Preserve the released landscape and random initialization.

Required fresh experiments remain:

- Full population trajectory and independent state/measurement checks.
- Sequential reference plus Lock-Based, TVar and TArray timing across 1–8 capabilities.
- Four implementations across all five rebirthing populations, with four capabilities for concurrent variants.
- TVar/TArray retry ratios across 1–8 capabilities, measured separately from timings.
- TArray carrying-capacity and rebirthing performance/retries at 16, 32 and 64 capabilities.

The paper's local machine was an i7-8550U laptop, Ubuntu 19.10, with GHC 8.4.3
and Stack resolver lts-12.4. Hardware changes prevent treating identical elapsed
seconds as an appropriate fresh-run criterion. Before confirmatory runs, freeze
hardware topology, resource isolation, repetitions, ordering and confidence-interval
comparisons for the paper's relative-performance claims. Do not infer physical core
counts from Haskell capabilities. No fresh-run acceptance criteria are finalized yet.

## Source fidelity

Use timing revision `f5851488bf2369e2bbdc3f2499ed69c142de9fec`.
All 61 model/build files match revision `b6c4aeccdc153f26edef9709764e055e4e36b806`,
which contains the completed local experiments.

Revision `6a79b8b2e623c288c087b91aff400ac2c4d95510` enables TArray retry instrumentation.
Its source explicitly warns of reduced performance. It is suitable for toolchain
validation and instrumented measurements, not the uninstrumented timing comparison.
Latest revision `2bf138a8b5f1d020f09781932e110091802f6dcc` additionally replaces the
sequential benchmark entry point with population CSV export.
[Revision hashes](results/archived/revision-fidelity.json) retain these distinctions.

The pinned `stm-stats-0.2.0.0` library computes retries divided by commits,
not retries divided by attempts. Its counters persist within the process;
record process boundaries and cumulative counts when interpreting repeated benchmarks.

## Reproduced archived analysis

The audit reads 53 complete author Criterion HTML reports, checks their SHA-256
hashes, and independently fits ordinary least squares to 212 raw measurements.
All regression slopes match within 1.99e-13 seconds. All 51 printed timing cells
in Tables 6, 8 and 9 match after rounding to three significant digits.
Parenthesized standard deviations and retry ratios are retained but not validated.

These are author archival measurements, not fresh simulation runs, independent
engine validation, or a hardware performance replication. The active Linux build
only verifies the original toolchain and executable availability.

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
Committed results retain individual raw-report paths, recomputed slopes, paper
cells, and limitations. Full raw HTML remains in the pinned original repository.
