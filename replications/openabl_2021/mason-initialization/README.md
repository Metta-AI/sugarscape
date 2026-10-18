# Native MASON initialization

All11 published MASON input sizes,250 through256,000 requested cells, match an independent reconstruction of the native seed-zero initial state. This covers4,072,272 fields. No C states overwrite these observations.

`initialize_mason.py` implements MT19937 seed expansion, twisting and tempering; the26/27-bit double conversion; bounded integer sampling with Java overflow rejection; and MASON19's1,249 discarded startup integers. It then constructs every cell using the generated model's six-significant-digit constants. These details were checked against the pinned MASON19 jar bytecode.

The native observer only calls `Sim(0).start()` and reads the resulting states. It performs no model steps. Every native initial snapshot, generated Java/class file, observer, validator, command, and audit is archived and byte-verified. The MASON dependency remains pinned by hash rather than bundled.

This validates seed-zero initialization under the reconstructed runtime. It neither recovers historical benchmark seeds nor establishes timing equivalence or complete model dynamics.

A complete225-cell comparison with an intentionally incorrect1,248-draw startup fails on five fields. This confirms that the audit detects a wrong startup random stream. The production validator retains1,249 draws.
