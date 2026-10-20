# Seventh unassigned-shard checkpoint

Fresh storage readback verifies the 11,919,037-byte checkpoint against its producer hash and every extracted member.
All 25 deposited configurations and qualified execution payloads match exactly; 125,025 observations pass raw trajectory audits.
The inputs are disjoint from the previous 1,055-input inventory.

Coverage reaches 1,080 unique inputs and 4,380,746 observations: 400 baseline and 680 sweep inputs.
The sweep still requires 9,420 audited inputs.
All result fields for Tables I–III remain unchanged except the inventory hash.
The complete Table IV row at 0.36–0.40 remains unchanged: 6 extinct, 0 worse, and 494 better across 500 inputs.
Incomplete rows receive no percentage estimates; this checkpoint does not complete the study.

The original bounded unassigned-shard producer continues unchanged.
The audit neither restarts simulations nor changes frozen input assignments.
The raw checkpoint remains in task storage at the destination recorded in `storage-intent.json`.
