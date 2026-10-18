# OpenABL Sugarscape replication (2021)

Paper: Cosenza et al., [Easy and efficient agent-based simulations with the
OpenABL language and compiler](https://doi.org/10.1016/j.future.2020.10.014).
[Accepted manuscript](https://eprints.whiterose.ac.uk/id/eprint/167728/1/_FGCS_5882__OpenABL__Cosenza_et_al__2020.pdf).

Status: incomplete. This study covers the paper's Sugarscape results, including
code size, cross-backend performance, and distributed scaling. Other models are
outside its scope. The 2018 conference version does not receive separate credit.
Historical dependency reconstruction and quantitative benchmark runs remain required.

## Source and workload

The [source audit](source-audit.json) pins OpenABL commit
`eb08ef86df0b9c0532cb8fd6b714bde5e8551923` and its Apache-2.0 license.
The model last changed in 2017. This does not prove which compiler revision or
dependency versions produced the paper's results.

[Released workloads](benchmark-workloads.json) contain 36 cross-backend
conditions at 100 steps. Requested cell counts round down to square grids.
The distributed script defaults differ from the journal's stated workload;
its million-cell, thousand-step experiment requires explicit overrides.
No historical speed comparison is justified on this Mac.

## Native execution and buffer diagnosis

[Build evidence](build-evidence/build-receipt.json) preserves original failures,
the integer-printer portability patch, successful compiler build, and generated
C compilation. The model is unchanged. Bison 3.8.2 and AppleClang 17 build the
compiler; GCC 16 builds generated C with the released optimization/OpenMP flags.

The first condition requests 250 cells, initializes 225, and executes 100 steps.
Two DSL `save` calls capture initialization and the final state. Native runs
with one and two OpenMP threads produce byte-identical snapshots.

After 100 steps, all native cell sugar, occupancy, metabolism, environment sugar,
and agent IDs equal their initial values. Only target positions change.
The C generator initializes its second buffer once, then swaps buffers without
copying unchanged fields. The MASON generator explicitly copies those fields.

A control adds four assignments to generated C, copying each input cell into
its output before the corresponding stage. Initialization remains byte-identical.
The control changes 171 cell IDs and 157 environment-sugar fields; occupied
cells decline from 31 to 25. Original output remains preserved.

`replay.py` independently executes all four stages from the saved initialization.
Both its stale-buffer and copy-buffer modes match all 1,800 final fields of their
respective native runs. This supports the buffer diagnosis for this condition.
It does not validate initialization randomness, every backend, or the paper's
historical results. No negative paper verdict or completion credit is assigned.

## Recheck retained evidence

The [native archive](native-condition/native-and-control.tar.gz) includes the
observed DSL, generated sources, binaries, logs, and all snapshots. Its receipt
records the hash; every archived member was compared with its native original.
Extract into a fresh directory, then run:

```sh
python3 replay.py evidence/threads-1/initial.json evidence/threads-1/final.json stale.json --steps 100 --buffer stale
python3 replay.py evidence/copy-control/initial.json evidence/copy-control/final.json copy.json --steps 100 --buffer copy
```

The retained `replay-stale.json` and `replay-copy.json` record input and replay
hashes, comparison scope, and zero differing fields. These are complete-model
execution audits, not isolated-function tests.

## Required next evidence

- Identify historical compiler and backend dependency revisions.
- Independently validate initialization and all stages across the declared workloads.
- Resolve buffer semantics across C, MASON, FLAME and FLAME GPU before timing comparisons.
- Reconcile extracted Sugarscape targets with historical experiment configurations.
- Reproduce code-size, cross-backend and distributed results with uncertainty and hardware limits stated.

## Native MASON control

[Native MASON19 evidence](mason-condition/comparison.json) uses the same225-cell
initialization as C, with both MASON state buffers explicitly initialized before
scheduling. The original four generated stages run unchanged for400 scheduler
steps, corresponding to100 model steps. A read-only observer captures live fields.

MASON finishes with25 occupied cells, matching corrected C in count, but48 agent
IDs and125 environment-sugar fields differ. Native neighbor traversal can change
first-candidate tie resolution; this remains an explanation to verify. Population
agreement alone does not establish backend equivalence.

The released MASON snapshot helper produces malformed JSON for nested state
objects. Its retained initial malformed output comes from the controlled start;
the preceding unseeded initial file was overwritten. The observer snapshots are
valid JSON and their225 initial cells match C exactly after sorting by position.
The jar URL/hash, generated Java, observer, logs and snapshots are retained.

## Neighbor-order control resolves this condition

[The separate ordering control](mason-order-control/comparison.json) sorts each
of the three MASON neighbor-query results by fixed cell coordinates. That
reproduces C array order. No stage rules, initial values, or scheduler settings
change. The original MASON run remains preserved.

All1,800 initial and all1,800 final fields now match corrected C after100 steps.
Neighbor ordering therefore accounts for the previous final-state mismatch in
this condition. The source chooses the first maximum-sugar neighbor and first
competing claimant, so traversal order affects ties. This is an experimental
control, not evidence that native backends are generally equivalent.

Both buffer copying and neighbor-order semantics must be addressed before
interpreting cross-backend timings. Historical workload reconstruction and all
other declared paper targets remain outstanding.

## Published target extraction

[Figure5 targets](paper-targets/targets.json) preserve seven printed Sugarscape
runtimes, visually checked against the accepted manuscript. Figure4 curves were
visually inspected but have not been digitized. Hardware differences require
separate interpretation; these values are not new-run acceptance margins.

[Code-size history](paper-targets/code-size-history.json) checks all14 recorded
model revisions. The released source has156 effective lines versus154 in
Table1. No recorded revision gives154 after removing comments and blank lines.
Exact author files and counting-tool behavior remain unresolved; no negative
verdict is assigned. The FLAME GPU345-line reference still requires provenance.

## Figure4 vector targets

[All36 curve points](paper-targets/figure4.json) are extracted from the pinned
PDF vector paths using `extract_figure4.py`. Legend identities and logarithmic
axes were visually checked. Every inferred input size lies within0.03% of a
250-times-power-of-two workload; nominal counts are retained alongside raw values.

MASON has11 points through256,000 cells, exceeding the released128,000 default.
C has7 points beginning at500 cells, omitting the released250-cell starting point.
FLAME has5 points and FLAME GPU13. These differences remain explicit; defaults
do not substitute for the published benchmark coverage.

Recorded coordinate sensitivity perturbs each y-coordinate and calibration tick
by0.001 PDF points. It is neither statistical uncertainty nor a new acceptance
margin. Extracted runtimes approximate the published plot, not original raw data.

## Historical FLAME GPU code-size match

[The reference count](paper-targets/flamegpu-code-size.json) reproduces345 lines:
134 in `functions.c` plus211 in `XMLModelFile.xml`, excluding comments and blanks.
Both files are pinned to the2016 commit `a9451facf34b067ec970ab23bc52960f37f22dc0`.
The2018 XML-formatting commit increases the total to360 lines. Canonical XML
comparison after whitespace removal finds identical model content.

This resolves how a historical reference can yield the published345-line value;
it does not establish the exact author checkout. OpenABL's154-line value remains
unresolved. The manual FLAME GPU reference is separate from OpenABL-generated
FLAME GPU benchmark code, so its behavior does not determine those timings.

## Independent initialization reconstruction

`initialize.py` reconstructs the released C generator's seeded xorshift sequence,
integer sampling, Gaussian resource map, occupancy, and initial wealth. It matches
all1,800 native initialization fields for the225-cell condition, consuming481
random draws. [The audit](native-condition/initialization-audit.json) records the
final generator state and input/source hashes.

```sh
python3 initialize.py evidence/threads-1/initial.json initialization.json --requested-cells 250
```

Together with the four-stage replay, this validates the complete initial-to-final
path for this condition. It does not establish equivalence at other sizes or
with MASON's different generator. The released integer generator omits the lower
offset for power-of-two ranges; that defect does not affect these default calls,
whose power-of-two ranges all begin at zero. The reconstruction preserves it.

## Complete published C grid behavior

[All seven C sizes](c-grid/README.md) execute100 steps and pass independent initialization and 100-step replay with endpoint comparison:502,648 fields at each endpoint. `replay.py` uses exact half-integer grid lookup while retaining native neighbor order. This removes the quadratic neighbor scan. Historical timing and other backend scopes remain incomplete.

## Complete C buffer-copy controls and initialization precision

[All seven copy-buffer controls](c-copy-grid/comparison.json) retain byte-identical native initial states and match502,648 independently replayed final fields. Only four buffer assignments differ from generated C.

[The precision investigation](initialization-precision/README.md) resolves22 initializer discrepancies at128,000 cells by preserving six-significant-digit generated constants. Ten retained initial-state conditions pass after the validator correction. No scientific model or acceptance tolerance changes. MASON comparisons at the two largest sizes remain running.

## Native MASON random initialization

[All11 published grid sizes](mason-initialization/README.md) pass independent reconstruction of4,072,272 native initial-state fields at seed zero. `initialize_mason.py` reproduces the pinned MT19937 generator and1,249-draw MASON startup. These observations retain MASON's own initialization; the separate C-initialized trajectory controls remain distinct.

## Complete published MASON grid controls

[All11 paired conditions](mason-grid/README.md) now execute100 steps. Each variant matches4,072,272 initial fields against the C initializer; the ordered-neighbor control matches4,072,272 independently replayed final fields. Native-order differences remain recorded at every size. Historical timings and other paper targets remain incomplete.

## Complete published FLAME grid behavior

[All five native FLAME sizes](flame-grid/README.md) now execute100 steps. Independent checks match60,600 initial and final fields; all765,075 native agent observations pass structural/resource audits. Pinned dependency reconstruction and the GCC16 common-symbol build flag are explicit. Historical performance and GPU/distributed validation remain outstanding.

## GPU execution and tie-order diagnosis

[The 225-cell GPU qualification](gpu-condition/README.md) completes 100 steps. Native repeats diverge despite identical initialization. Fixed-position tie-breaking matches all 180,000 independently replayed transition fields. Native results, failed attempts and the diagnostic patch are retained separately. Larger GPU conditions and historical timings remain incomplete.
