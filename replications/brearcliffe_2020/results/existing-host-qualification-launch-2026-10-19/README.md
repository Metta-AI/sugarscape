# Qualification moved to existing owned capacity

The original queued host never started. Its boot command was canceled, its local uploader terminated, and its queue entry withdrawn before launching the replacement.
The provider reports no resource created or billed for that queue entry.

Initial command `cmd-u7rgn` installed Java but exited before simulation: this image has no `python3` on PATH.
Recovery `cmd-k93u9` uses the existing Python 3.11.14 interpreter and requires an absent results directory before starting.
The unchanged payload pins the author model, recorder, NetLogo 6.1.1 libraries, and two full-length reference trajectories.
Ubuntu 22.04 OpenJDK 11 replaces the planned Temurin image; exact trajectory qualification remains mandatory.
Each case runs 20,000 steps sequentially with 1 GiB Java heap and a 1,800-second limit.
Recovery has a 3,720-second limit plus 30-second termination grace, within the original 5,100-second placement budget.
The conservative original compute-plus-idle ceiling is $1.21.

This is a launch record, not successful qualification or an ensemble result.
Ensemble dispatch still requires both comparisons to pass and a budget based on measured runtime.
The embedded payload plan retains original host metadata; the wrapper plan here defines actual placement and budget.
