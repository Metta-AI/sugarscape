# Baseline recovery terminal reconciliation

The original bounded command is terminal with exit1 after the preserved native timeout.
Both sealed checkpoint archives were freshly downloaded from task-owned storage, verified against sealed hashes, and independently audited.
Every original input, source/runtime manifest, full trajectory, terminal receipt, and archive member is checked.

All41 attempts are accounted for:40 full trajectories exactly match retained original hashes, and one failed partial file matches the preserved timeout bytes.
The successful inputs contain108,322 observations. Twenty-two successes were already counted; exact duplicate records are verified and counted once.
This adds18unique inputs and56,307observations, bringing coverage to237inputs and1,069,333observations.
There are107audited baselines and130sweep inputs;293baselines and9,970sweep inputs remain.

The293unfinished original baseline rows comprise one failed input and292unstarted inputs.
They are retained in original order in reconciliation.json, disjoint from every audited input.
No failed or partial output receives credit. A subsequent recovery needs a separate bounded plan informed by the retained runtime diagnosis.
The old command is not restarted or extended. This terminal batch audit does not complete the paper.
