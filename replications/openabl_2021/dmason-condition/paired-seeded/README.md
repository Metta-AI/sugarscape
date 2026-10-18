# Paired initialization and ordering controls

All four two-partition conditions use seed zero, 3,969 cells and 100 four-stage
steps. Initial fields match exactly across conditions. Independent MT19937 and
MASON-startup reconstruction also matches all 31,752 initial fields.

With native neighbor ordering, the identity-hash control changes 4,647 final
fields while both variants retain 297 occupied cells. That comparison alone
cannot separate hash identity from changed neighbor order.

A second pair sorts each of the three neighbor bags by fixed `(x,y)` position.
Both native identity and corrected hashing then match every final field of the
independent copy-buffer replay: 31,752 fields each, zero differences between the
pair. The native field still contains 4,999 records for 3,969 positions; corrected
hashing contains 3,969. Duplicate records agree in every observed state field.

Thus the duplicate field representation does not change these deduplicated
scientific results under controlled ordering. This does not prove native
ordering equivalence, native timing comparability, general safety of mutable
identity hashes, or the full distributed scaling experiment. Joined-worker
lifecycle observation, fixed seeds, hash changes and neighbor sorting remain
explicit controls, not replacements for released behavior.

Sources, classes, initial/final states and logs are retained in the archive.
Every member matches its original byte-for-byte. Scientific study completion
remains unclaimed.
