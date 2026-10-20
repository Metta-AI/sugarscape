# Prospective trade/lending horizon extension

The original 500-step comparison retains a substantial population trend, so its final-window mean does not establish carrying capacity.
This diagnostic extends the unchanged released model to 10,000 steps.
It preserves all three original configurations and uses the first seed, 14133, from the existing twenty-seed comparison.
The horizon and analysis windows are analyst choices, not recovered historical settings.

The pilot runs baseline, trade, and lending sequentially, with a 900-second bound per process and at most 2,700 simulation seconds.
Execution uses the original Python runtime, source hashes, and random-seed controls.
Acceptance requires exact equality of every original trajectory field through step 500, not merely population agreement.
The runner halts on a failure; there is no automatic retry or horizon reduction.

The independent audit requires all three completed conditions, validates source/configuration and trajectory hashes, and checks native timestep/population/extinction invariants.
It reports all ten consecutive 1,000-step population means and paired means over the fixed interval 5,001–10,000.
Only population receives an absorbing-zero extension after extinction, because agent replacement is disabled.
Remaining drift is reported without selecting a favorable window or fitting a tolerance to the paper's percentages.

The retained scripts are exact execution evidence and contain this workspace's paths.
The pilot is running; no results, stationarity verdict, twenty-seed inference, or paper-completion credit are assigned here.
Full-cohort continuation requires successful prefix qualification and an explicit bounded execution plan.
