# Sixth runtime checkpoint audit

Each cohort retains four things: full per-group audits, the original transport
receipt, new completed inputs, and original checkpoint metadata. Reconstruct
using `reconstruction.json`: the preceding base archive, preceding delta, this
new-input delta, and checkpoint metadata. Decompress missing trajectory JSON
files from gzip and verify existing raw files agree.

The full auditor is `audit_runtime.py`; use the original archive ZIP and the
recorded root in each original command. `coverage.json` reconciles all prior
audits by original archive entry, with byte-identical overlapping record values.
Zero-coverage groups are explicit. The completed 100-input altruistic group does
not establish the paper's separate 500-seed claim.
