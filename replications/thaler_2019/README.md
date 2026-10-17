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
concurrent execution delegates ordering to the scheduler. The sequential implementation
shuffles the environment behavior together with agents. Concurrent implementations
run growback synchronously after the population. Performance runs use 1,000 steps and seed 42.
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
All 53 archived sample standard deviations also reproduce from the raw per-iteration timings.
Of 45 printed standard deviations, 30 match rounding to the nearest hundredth; 15 differ.
The largest absolute difference is 0.008984 seconds. These reporting differences remain explicit;
no alternative tolerance or negative paper verdict is assigned. Table 9 parentheses are retry ratios,
which cannot be reconstructed from these timing samples and remain unvalidated.

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

## Population target fixed before native execution

Figure 5b contains a raster curve rather than vector coordinates or raw measurements.
The pinned PDF embeds a 1412×830 image on page 18. We visually checked the plot,
calibrated both axes from tick centers, and extracted the blue curve separately
from axes and labels. The resulting 50 targets span times 0–49, falling from
approximately 500 to 206 agents.

The [frozen protocol](results/population-target/target-protocol.json) accepts a maximum
absolute difference of two agents at every time point. This allows raster line width,
antialiasing and axis calibration uncertainty. It was fixed before any fresh native
population output. These targets are digitized measurements, not author raw data.
The caption does not specify a seed; the released population exporter uses seed 42.
A mismatch requires checking revision, seed, time indexing and model semantics.
No population replication result is available yet.

Recreate the target with Python, PyMuPDF 1.26.5 and NumPy 1.26.4:

```bash
python replications/thaler_2019/extract_population_target.py \
  /path/to/s40294-019-0067-9.pdf /path/to/new-target-directory
```

The output includes the original embedded figure, every extracted pixel-column
measurement, interpolated population targets, calibration and artifact hashes.

## Scheduling and population measurement audit

The [source audit](results/archived/scheduling-audit.json) checks 11 files against the
pinned timing revision. Sequential `Init` inserts the environment as behavior ID 0;
`Simulation` shuffles that behavior with agents. Concurrent `Main` sets `envConc=False`,
and `Simulation` waits for all agents before stepping the separate environment.
Thus the released variants do not share the same growback schedule. Preserve this
difference for faithful replay; investigate its effect before attributing performance
changes solely to synchronization.

Sequential agents consume metabolism and die, if necessary, before moving and
harvesting. Surviving agents emit observables; the environment emits none. The released
population exporter counts those observables. Its times 0–999 label post-step outputs
using the pre-increment clock. Do not prepend an initial-state row or shift times when
comparing the first 50 rows with Figure 5. These source findings establish measurement
semantics, not a fresh simulation result or a negative replication verdict.
