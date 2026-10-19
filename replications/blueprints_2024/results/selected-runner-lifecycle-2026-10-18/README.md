# Native workflow lifecycle verification

The replacement runner owns one process group per original input.
It terminates the whole group on input deadlines, batch deadlines, and SIGTERM,
then checks that no live group remains before returning a terminal result.
Incomplete allocations return 124; fully completed allocations return zero.
The input scripts and original scientific configurations are unchanged.

Four final workflow controls use the real pinned simulator: input deadline,
batch deadline, two concurrent inputs interrupted by SIGTERM, and a completed original input.
All expected exit codes, declared completion states, and empty terminal process-group checks pass.
Original raw input 60 completes through natural extinction at timestep 116.
Its full trajectory hash exactly matches the previously audited original result.
This repeated input adds no scientific coverage.

The archive also preserves failed preliminary controls.
Raw input 0 exceeded its 180-second operational limit; it is not a successful run.
An initial completed-run control exposed a stale process snapshot after reaping a finished parent.
The final runner refreshes that snapshot before deciding whether live descendants remain.
Every archived file was compared byte-for-byte; the receipt records its hash and size.
These controls verify native workflows on macOS. Linux qualification remains required before cloud production.
