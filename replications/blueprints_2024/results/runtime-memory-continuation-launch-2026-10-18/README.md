# Bounded continuation with additional memory

The prior batch is terminal; all completed and failed outputs are preserved.
Command `cmd-tirtj` is registered for the task-owned CPU8 node's next readiness event.
It resumes only raw 50,000-step indices `[55,100)` and altruistic indices `[3,100)`.
These intervals do not overlap the separately running Bentham 50,000-step workers.
The original model, archive inputs, Python version and native runner remain pinned unchanged.
A fresh output directory preserves all prior failures.

The previous two-worker batch hit its 8 GiB container limit.
This continuation requires at least 32 GiB before starting either of its two workers.
GNU time records each group's maximum resident memory, including native children.
That measurement is a maximum, not the sum of simultaneous memory use.
It improves diagnosis but does not guarantee that the larger allocation suffices.

Each group has six hours; setup and execution have a 23,400-second shell bound.
The provider additionally enforces 391 minutes after wake, and the queue hold is two hours.
At the quoted $0.576/hour, the maximum execution plus final idle window is $3.8976.
Completed-output checkpoints are sealed every thirty minutes and exported to owned object storage.
The collector has a 34,200-second deadline and cumulative 2 GiB export cap.

The native runner is unchanged. The orchestration change adds a GNU time wrapper,
strict paired-plan iteration, and formatting. Full study completion still requires all declared inputs.
Pending registration is not execution or validation evidence.
