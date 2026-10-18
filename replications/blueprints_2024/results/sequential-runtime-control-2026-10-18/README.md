# Sequential runtime control, in progress

Two original 5,000-step selfishness inputs (0.0 and 0.5, seed 158402133555746433) run in CPython/PyPy/PyPy/CPython order on one owned CPU-2 node. All eight complete trajectories must match previously audited hashes. This checks timing and memory without concurrent simulations on this node; shared-host scheduling can still affect timing.

The engine remains v2024.1. Only logfile paths change. CPython 3.11.14 and PyPy 7.3.20 / Python 3.11.13 are pinned; the PyPy archive hash is verified. Live readback confirms one simulator, the exact first input, and both runtime versions. No equivalence or speedup result is claimed yet.

`cmd-vkkmk` started at 19:59:29 UTC. Simulation time is bounded to three hours, with a 210-minute outer bound. Estimated compute plus idle cap is approximately $0.55, excluding the short interrupted setup attempts. Terminal evidence export is bounded to 512 MiB and twelve hours.

The first registration became active during cancellation. Its nested timeout process group survived the API command kill, leaving a simulator running. Live process inspection found this overlap with the second attempt. Both task-owned attempts were stopped; their partial outputs remain preserved and are excluded from timing and scientific completion.

The fresh runner verifies no existing simulator before launch. It gives each timed simulator a process group, kills that group before archiving on interruption/timeout, and handles SIGTERM through the same cleanup. The second attempt's interruption exited 130 and sealed evidence; the first attempt's files remain on the node. Registration state alone did not establish process termination.

This is a runtime qualification control, not a paper result or authorization to substitute runtimes throughout the remaining sweeps. Existing independent controls remain retained.
