# Complete published MASON grid controls

All11 published MASON sizes,250 through256,000 requested cells, execute100 model steps with the pinned MASON19 jar and Java17. Both variants start from the same verified released-C states. All4,072,272 initial fields match in each variant.

The control sorts the three neighbor bags by fixed x/y position; native model stages and scheduling remain unchanged. Independent copy-buffer replay matches all4,072,272 ordered-control final fields. Native neighbor order produces a different final state at every tested size; exact per-field counts remain in the comparison. These are controlled deterministic outcomes, not estimates over random seeds.

The first nine sizes completed before the128,000-cell initializer found22 discrepancies. Reproducing the compiler's rounded constants resolved that validator error. The final two sizes then ran in a new directory; the repeated128,000-cell C initialization is byte-identical. No failed result or difficult input is excluded.

The archive preserves both generated Java variants, native outputs, initialization tables, observer, source pins, commands, replay audits, and separate launch protocols. Every member matches its retained source byte-for-byte.

MASON's own seed-zero initialization is validated separately in `../mason-initialization`. Historical compiler/dependency provenance, timings, other backends, and distributed scaling remain incomplete.
