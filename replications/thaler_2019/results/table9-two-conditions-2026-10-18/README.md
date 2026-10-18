# Two accepted Table 9 conditions

The sealed checkpoint contains two of six required timing conditions. Independent
least-squares reconstruction verifies eight raw measurements and both accepted fits.
The 16-capability, 2,500-agent rebirth condition yields 66.010451 seconds per
simulation, R-squared 0.999935623439. The earlier 32-capability condition remains
89.962304 seconds. Both pass the predeclared fit criterion on their first attempt.

These are partial native measurements on AMD EPYC 7571, with verified allocation,
source archive and timing-binary hashes. Historical clock and host-isolation
equivalence remain unproven. Four timing conditions and all thirty retry processes
remain required; the original producer continues without restart.

Extract the checkpoint, place the separately pinned source-f5851488.tar.gz beside
its results directory, and run audit_table9.py with --timing-prefix. The source
archive is reused from the first checkpoint evidence after verifying its hash.
