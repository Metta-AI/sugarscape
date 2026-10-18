# OpenABL Sugarscape replication (2021)

Paper: Cosenza et al., [Easy and efficient agent-based simulations with the
OpenABL language and compiler](https://doi.org/10.1016/j.future.2020.10.014).
[Accepted manuscript](https://eprints.whiterose.ac.uk/id/eprint/167728/1/_FGCS_5882__OpenABL__Cosenza_et_al__2020.pdf).

Status: incomplete. This study covers the paper's Sugarscape results, including
code size, cross-backend performance, and distributed scaling. Other models are
outside its scope. The 2018 conference version does not receive separate credit.
Full figure extraction and historical dependency reconstruction remain required.

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
- Extract every Sugarscape figure target and its experiment configuration.
- Reproduce code-size, cross-backend and distributed results with uncertainty and hardware limits stated.
