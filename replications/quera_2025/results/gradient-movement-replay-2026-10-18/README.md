# All 256 gradient-baseline trajectories independently replayed

The unchanged submission model executes the original diagnostic seeds 3–258,
with 100 agents, a 50×50 grid, vision 1/3 and 25 stored states.
The configuration matches the retained expectation-gradient ensemble, including
all six parameter values, Gaussian smoothing and the gradient horizon.

An ordinary native pass and a passive activation-order trace produce identical
serialized state-component hashes for every seed. This checks 1,536 histories,
containing 34,560,000 scalar state values. All 115,200 retained aggregate records
match native baseline wealth exactly. Native execution exits zero in 55.07 seconds.

Independent Python replay reconstructs **614,400 agent updates and 15,360,000 cell
updates**, with maximum absolute state error zero. All realized destinations
maximize the source’s masked score; harvesting, metabolism, prior-wealth survival,
occupancy and regeneration also match. Random tie-selection probabilities are
not independently reproduced.

Among 585,140 live-agent moves, 6,041 have maximum candidate score zero.
There are 4,020 moves outside the vision mask and 223 into cells marked occupied.
These categories can overlap. Every exceptional move has zero maximum score;
all 256 seeds contain an outside-mask move. The source multiplies unavailable
locations by zero, allowing them to tie with permitted zero-resource locations.
Each exceptional event is retained in `audit.json`.

This extends the earlier calibration-pilot finding to the complete baseline
population of the reconstructed gradient diagnostic. It does not replay the
perturbed finite-difference trajectories, prove every differentiated state,
identify the paper’s exact Figure 11 protocol, or reproduce calibration.
No source rule is corrected and no completed-paper credit is assigned.

## Reproduction and controls

Extract `native-evidence.tar.gz` into a fresh directory. `archive.json` retains
its SHA-256 and confirms every archive member matched the native output.
Use the unchanged Julia 1.11.3 depot and pinned source documented by the study:

```sh
julia --startup-file=no --project=DIFFABM trace_gradient_movement.jl DIFFABM NEW_OUTPUT ORIGINAL_GRADIENT_ENSEMBLE
python replay_movement.py EXTRACTED/native ORIGINAL_GRADIENT_ENSEMBLE NEW_AUDIT --profile gradient-ensemble
```

The gradient ensemble is retained in `../gradient-ensemble-2026-10-17`.
The generalized replay also reproduces the earlier three-seed calibration audit:
14,700 agent updates, 91,875 cell updates and seven outside-mask moves, with zero
state error. A separate derived-data control omits the last seed’s cell file;
the public audit fails and produces no result. Original evidence remains intact.
