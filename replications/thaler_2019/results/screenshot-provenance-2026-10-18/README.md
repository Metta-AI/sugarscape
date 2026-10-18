# Figure 5a provenance remains unidentified

The existing observer qualification contains two native 1,000-step runs per implementation.
At both times 49 and 50, sequential counts are 206 and 206; IO counts are 203 and 201;
TArray counts are 207 and 204; TVar counts are 206 and 207.
All use the declared seed 42 and 500-agent, no-rebirth configuration.
Concurrent variants use one capability and still differ between fresh processes.

The image contains 201 occupied cells. One IO count equals that number, but no corresponding
spatial state was exported. This equality neither reproduces the image nor identifies its implementation.
No seed, time, tolerance or configuration was selected to improve agreement.

The tracked sequential Main, GlossRunner and Renderer histories contain only their initial 2019-10-11 commit.
The committed Main configures 2,000 agents, rebirth enabled and graphical output disabled;
it therefore does not authenticate the paper screenshot configuration.
The graphical callback invokes the same simulation step and ignores the wall-clock delta argument.
The prior native graphical-model control remains the relevant source-difference check.

Source hashes, tracked history and the eight native CSV hashes are retained.
The image implementation, source revision, configuration and concurrent schedule remain unresolved.
The required timing and population ensembles remain separate and are still running.
