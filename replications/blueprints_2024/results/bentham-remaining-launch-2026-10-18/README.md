# Disjoint remaining Bentham allocation

The new CPU-only node has 152 required original inputs.
These exclude every already audited input and all 19 unfinished inputs reserved for the live local retry producer.
The original configurations, seeds, release, and 5,000-step horizons remain unchanged.
Eight workers have 7,200 seconds per input and 21,600 seconds for the batch.
The platform bounds the entire boot command to seven hours, including setup and qualification.
At the recorded rate, including a 15-minute idle window, the estimated maximum cost is $4.18.

The node was queued when this record was written; no production result is claimed.
Its single boot command is registered, and the free queue hold is eight hours.
Before production, Linux must pass the real-input deadline, interruption, and completion controls.
The completed qualification trajectory must exactly match the independently retained original hash.
Any failed qualification prevents production from starting.

The payload pins Python 3.11.14, Pydantic 2.12.3, the original archive hash,
and source release b9ca671ab7591c7b3606f2d76c33eda344d626d1.
The new runner verifies descendant termination before terminal sealing.
All incomplete and partial outputs remain preserved; they receive no completion credit.
A task-specific collector is registered to export the sealed terminal archive to the existing owned evidence bucket.
Its observation deadline is 12 hours; a long queue may require continuing that collector without restarting production.
