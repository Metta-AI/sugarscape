# Observable agents versus occupied cells

Source inspection identifies a distinction our earlier population summary obscured.
The exporter counts returned agent observables, not occupied cells.
Dying agents emit no observable. Replacement agents occupy a cell immediately but first emit their own observable on a subsequent step.
The simulator constructs observations and replacement threads separately.
All five inspected model modules match the pinned timing revision exactly.

The reported 2,320 TArray observations under 2,500-agent rebirth therefore do not establish 180 vacant cells or lost agents.
The earlier raw measurements remain valid; their population interpretation requires correction.

A four-run native qualification exports both counts after forcing the complete original simulation output.
It preserves seed 42, 1,000 steps, one capability, and original initialization/model loops.
Two normal runs use 500 agents; two rebirth runs use 2,500.
No timing claim or statistical-equivalence margin is introduced.

The local attempt stopped before simulation because the compiler cache was unavailable and installation consumed remaining disk capacity.
Its logs and terminal state remain retained.
The earlier CPU8 task node reports no restorable disk; it was not restarted or deleted.
A fresh CPU2 node runs command `cmd-573ts`, bounded to 5,400 seconds.
At $0.0024/minute plus 15 idle minutes, the quoted bound is $0.252.
A bounded collector exports terminal evidence to task storage; results remain pending.
