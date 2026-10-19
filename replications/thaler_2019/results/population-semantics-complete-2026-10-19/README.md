# Native observation-semantics validation

Four original TArray runs complete 1,000 steps each under GHC 8.4.3.
All 4,000 observations pass the independent audit; a second audit reproduces both result files byte-for-byte.
Prepared source hashes, launcher bytes, compiler, exit records, and completed export receipt verify.

Both 2,500-agent rebirth runs retain exactly 2,500 occupied cells throughout.
Their observable count ends at 2,320 and reaches a minimum of 2,207.
The measures differ at 999 of 1,000 steps, with a maximum gap of 293.
Both rebirth CSVs are byte-identical.
The two normal runs have equal observable and occupied-cell counts at every step, ending at 189 and 186.

This validates the corrected interpretation: missing newborn observations are not missing occupied cells.
The original model and initialization remain unchanged; the exporter adds a count after forcing the simulation outputs.
This is a TArray observation-semantics result, not proof for every implementation or a performance replication.

The complete 70,070-byte native archive is included.
Run `audit_population_semantics.py native.tar.gz export-intent.json NEW_OUTPUT` to reproduce the audit.
The original local preparation failure remains in the launch evidence.
