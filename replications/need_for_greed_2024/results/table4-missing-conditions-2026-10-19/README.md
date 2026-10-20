# Missing conditions for Table IV

The 0.36–0.40 bin requires 500 original inputs: five conditions with 100 seeds each.
The original 100 inputs at 0.37 are already audited.
This batch freezes exactly 400 remaining inputs at 0.36, 0.38, 0.39, and 0.40.
All configurations match both original deposits byte for byte and retain the 5,000-step horizon.
None overlaps the audited 0.37 cohort or six reserved endpoint controls.

The existing task-owned eight-CPU node accepted detached command `cmd-p6ykh` after restoring its disk.
The first launch request failed locally because 1,800 seconds exceeded the CLI's wake-wait ceiling.
Its rejection is preserved; the corrected request uses a 300-second wake wait.
The first command failed before simulation because restoring the base image removed system `git`, needed for the native revision check.
Its 7.650063-second failure and exported terminal evidence are preserved.
Fresh recovery `cmd-6ga7k` restores `git`, retains all inputs, and uses a new directory.
Its outer limit is reduced by 60 seconds to 32,340, keeping cumulative execution below the original bound.
The first CPython pilot is now producing trajectory data; bulk gates and all outcomes remain pending.
No simulation or paper completion credit is claimed.

Two original smallest-seed configurations, at 0.36 and 0.40, must complete under both CPython and PyPy with identical full trajectories.
Only then may eight workers process the remaining frozen inputs.
The batch uses the previously exercised Blueprints runner and independent trajectory auditor because the deposited inputs are identical.
The batch coordinator changes only its total simulation budget from the earlier bounded cohort.
Pilot outputs count once toward the 400-input cohort; native references are retained separately.

Bounds: 1,800 seconds per input, 30,600 seconds total simulation time, and 32,400 seconds for the outer process.
The declared conservative setup/export/idle allowance is $7.02 at no more than $0.012 per minute.
No automatic retries or budget extensions are authorized by this batch protocol.
The documented manual setup repair retains the original cumulative allowance.
The collector is bounded to 34,200 seconds and 2 GiB of exports.
Every 25 completions produces a sealed checkpoint; failures and partial outputs remain retained.

`payload-readback.json` verifies all 407 staged regular files, including the 400 unchanged configurations.
`payload.tar.gz` is the exact launch payload. Source archive and per-input hashes are recorded in `protocol.json`.
The terminal result, fresh artifact readback, complete trajectory audits, and Table IV comparison remain required.

The prospective Table IV target is 1.2% extinct, 0% worse, and 98.8% better: 6/0/494 of the full 500 inputs.
Paper-defined equality counts as worse; the released strict-less-than convention will be reported separately.
