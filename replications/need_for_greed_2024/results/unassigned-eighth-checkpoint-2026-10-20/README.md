# Eighth unassigned-shard checkpoint

Fresh storage readback verifies the 11,893,581-byte checkpoint against its producer hash and every extracted member.
All 25 deposited configurations and qualified execution payloads match exactly; 125,025 observations pass raw trajectory audits.
The inputs are disjoint from the previous 1,080-input inventory.

Coverage reaches 1,105 unique inputs and 4,505,771 observations: 400 baseline and 705 sweep inputs.
The sweep still requires 9,395 audited inputs.
All result fields for Tables I–III remain unchanged except the inventory hash.
The complete Table IV row at 0.36–0.40 remains unchanged: 6 extinct, 0 worse, and 494 better across 500 inputs.
Incomplete rows receive no percentage estimates; this checkpoint does not complete the study.

The original bounded producer continues unchanged. No simulations were restarted or frozen input assignments changed.
The raw checkpoint remains in task storage at the destination recorded in `storage-intent.json`.
