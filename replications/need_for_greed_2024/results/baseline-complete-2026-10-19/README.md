# Complete original baseline census

All 400 original baseline inputs are audited, including 100 raw controls.
The final checkpoint adds 18 disjoint inputs and 56,276 observations.
The shared inventory now contains 705 inputs and 2,558,145 observations: 400 baseline and 305 sweep inputs.

| Published table | Original inputs | Extinct | Worse | Better |
| --- | --- | --- | --- | --- |
| I: altruistic | 100 | 67% | 2% | 31% |
| II: egoistic | 100 | 62% | 2% | 36% |
| III: utilitarian | 100 | 0% | 0% | 100% |

All three rows match the published percentages exactly. No parameter or measurement adjustment was required for this agreement.
Independent R selects the 300 table inputs directly from the original ZIP and checks both classification conventions.
Those inputs contain 880,499 observations. No final population equals the initial population, so the two conventions agree here.
The Python baseline report repeats byte-for-byte; commands and its hash are retained in `repeat-validation.json`.
`verify_baselines.R` accepts the original ZIP, reconciled inventory, Python report, and output path.

The producer `cmd-ddr79` exited successfully at 2026-10-19T22:32:07.884431Z with all 293 assigned recovery inputs verified.
A fresh download of the entire terminal archive passes an independent audit of 293 inputs and 623,183 observations.
Every terminal-archive trajectory record matches the reconciled inventory exactly. This backup audit adds no duplicate coverage.
Both downloaded archives have their sizes, hashes, and durable object locations in `storage-readback.json`.

The original paged collector stopped after observing producer termination and retained checkpoints 0001–0011, missing checkpoint 0012.
A bounded filesystem export recovered the sealed final checkpoint and terminal archive without restarting simulations.
Later paged reads expose all twelve snapshots; the exact cause of the earlier incomplete log read remains unproven.
Earlier timeout evidence and recovery limits remain preserved in their dated result folders.

The original simulation inputs and source are unchanged. The recovery changed execution time limits, not the scientific method.
Table IV remains incomplete at 302/500 in its current five-level bin; 9,795 sweep inputs remain unaudited.
The death-rate figure definition is still unresolved. Exact baseline agreement does not settle those method questions.
Completion will be assessed by faithful implementation and execution of the method, independently of numerical agreement.
