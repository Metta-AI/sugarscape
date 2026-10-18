# GPU execution and ordering control

The released OpenABL Sugarscape model runs 100 steps on an H100 using FLAME GPU
`71ed81b1045581698f3618c585ee78ca0128c537`, CUDA 11.8 and GCC 11.4.
250 requested cells produce 225 actual cells. This does not complete the paper.

The original build fails because bundled CUB conflicts with CUDA's Thrust.
Putting `/usr/local/cuda/include` first in `CONSOLE_INCLUDES`, with `SMS=90`,
compiles without changing engine or model source. Both builds and their logs
are retained. This historical engine revision is not verified as the author's
exact revision. Modern hardware/compiler results are not historical timings.

All 1,800 initial fields match independent C RNG reconstruction. Across the
native run, its repeat and an ordering control, 303 snapshots contain 68,175
agent observations. Iterations, positions, capacity, state range and resource
bounds pass checks. The native run differs from copy-buffer C replay in 415
final fields. Repeating the same binary and initialization first diverges at
step 12 and differs in 389 final fields.

The generated engine enables `FAST_ATOMIC_SORTING`; message-bin ordering uses
`atomicInc`. The model chooses the first equal-sugar destination and the first
competing requester. The diagnostic patch selects the lowest fixed `(x,y)`
position in both ties, matching the independent C copy-buffer replay order.
All 100 controlled transitions match independently: 180,000 compared fields.
This identifies ordering sensitivity in this condition. The control changes
tie semantics and is not substituted for native paper replication evidence.

The first repeat attempt omitted `iterations/`. The released runner continued
and returned success despite failing to save its initial state. Its output is
preserved in `ordered-and-failed-repeat.tar.gz` and excluded from the audit.
The corrected repeat has its own archive. Likewise, the first build's archive
trap used the generated directory; explicit recovery preserved that failure.

OpenABL times the whole runner, including initialization and XML output. All
101 native snapshots were retained; the 0.58-second observed wall time is one
qualification measurement, not a reproduced benchmark distribution. Full GPU
size coverage, historical timing and distributed experiments remain open.

`file-receipts.json` verifies public copies against retained native artifacts.
`ordered-transition-audits.json` contains every transition comparison.
`audit-source.py` records the executed external-evidence audit with its original
paths; the archive names here are mapped in the receipt list and this document.
