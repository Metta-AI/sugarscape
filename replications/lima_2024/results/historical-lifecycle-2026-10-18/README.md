# Historical saved-agent lifecycle

The paper's reference 32 (page 56) records repository access on October 26,
2022. Commit `502d385` is the latest ancestor of our execution pin before that
date. It is a historically relevant candidate, not proof of the experimental
revision. Retained source files come directly from Git; hashes and paths are
recorded in `audit.json`. No historical execution is claimed.

The 2022 factory selects an existing `list/ID.asl` file or starts `miner3.asl`.
After delivering gold, that miner increments its score and adds `initial_print1`.
The corresponding active plan saves the agent and requests departure without
removing that belief. The 2023 source preserves this lifecycle. Its labels and
random test belief changed, so the full files are not byte-identical.

Page 52 claims restoration of prior agent information. It does not specify a
second gold delivery or score increment on reentry. Thus our frozen score-2
control still fails, but that failure alone does not contradict this published
claim. Native reload audits separately establish preserved beliefs and 39 plans.

This narrows the lifecycle uncertainty: the relevant source behavior predates
submission. It does not resolve all revision/dependency differences or establish
whole-paper replication. The older complete architecture has not been executed.
