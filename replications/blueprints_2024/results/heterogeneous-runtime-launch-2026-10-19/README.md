# Heterogeneous CPython/PyPy qualification launch

Three existing original controls cover 1, 50 and 99 utilitarian entries in the 100-entry model list.
Each runs under pinned CPython 3.11.14 and PyPy 7.3.20, retaining the full 5,000-step horizon.
Six concurrent native runs must pass independent trajectory audits and byte-identical paired trajectories.
No new unique-input coverage is expected because all three inputs were already audited under CPython.
Concurrent timing is recorded but cannot establish isolated throughput or whole-sweep equivalence.

The owned eight-CPU node resumes with command `cmd-s893e`, verified running after dependency restoration.
The platform limit is 121 minutes, each simulation limit 90 minutes, and archived output limit 1 GiB.
At the recorded $0.012/min rate, compute plus a 15-minute idle window is bounded to $1.632.
A four-hour, 1 GiB collector exports the sealed evidence to task-owned storage.
The first registration was rejected because on-wake commands require detached mode; that failure remains preserved.
A fresh process check confirmed no pending duplicate before the corrected registration succeeded.

This is a running qualification, not a result. Original controls, source hashes and runtime versions are frozen in `protocol.json`.
