# Unassigned sweep preparation

The current inventory leaves 9,597 original sweep inputs outside both audited coverage and the existing 400-input assignment.
All 9,597 configurations match both deposited archives byte-for-byte. Nineteen disjoint batches contain 505 or 506 inputs each.
The prepared partition excludes 230 audited sweep inputs and 273 unfinished inputs reserved by the current assignment.
No node, capacity reservation, or simulation has been started by this preparation.

## Proposed bounded execution

- At most four concurrent eight-CPU batches; no GPUs required.
- Each input has a 1,800-second native limit, with failures retained and not counted as successful.
- Each batch admits work for at most 41,400 seconds, counted from before setup and runtime qualification.
- The outer command is limited to 42,800 seconds plus 30 seconds kill grace. Qualification is inside this bound.
- Allow 1,800 seconds for export and 900 seconds idle time per batch; all attempts count against the total cap.
- At the observed $0.012/minute eight-CPU rate, the conservative per-batch allowance is $9.106; nineteen allowances total $173.014.
- Proposed overall cap: $175. Recheck price, live IDs, input ownership and remaining budget before every dispatch. Stop admission if the bound cannot be reserved.

The 100-run selfishness-0.37 timing sample averages 518.974 seconds. Extrapolating gives 172.94 eight-CPU node-hours and $124.51 before overhead.
This single-condition estimate is not a completion guarantee. Some conditions may be slower; a timeout or exhausted cap leaves work incomplete, without automatic extension.
New hosts must pass the previously established full-trajectory runtime qualification before bulk work.
The allocation and runtime must enforce the recorded outer bound across setup, qualification and execution, not grant separate extra time to those stages.

## Verification

The complete sweep partitions into 230 audited, 273 assigned-but-unfinished, and 9,597 unassigned inputs, with no overlap.
All twenty generated files repeat byte-for-byte after a preserved JSON key-order correction; semantic plan values and all batch inputs were unchanged.
`validation.json` pins the generator; `prepared/plan.json` pins the original inputs, current inventory, active assignment and all nineteen batch manifests.

Run `prepare.py` in a fresh directory directly beneath the retained evidence tree to regenerate the manifest set.
The rate observation queries only this task’s existing CPU node. It is not a reservation or guaranteed future price.
This preparation adds no simulation coverage or paper completion credit.
