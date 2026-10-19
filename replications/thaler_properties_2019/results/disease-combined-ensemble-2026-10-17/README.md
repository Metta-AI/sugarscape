# Combined disease correction ensemble

This package covers first seed zero, retained indices 1–67, and disjoint
continuation indices 68–99. All manifests and ledgers retain their original bytes.
The earlier batch exited at its disk guard; its terminal receipt pins the ledger.

Extract all three archives together. Restore each omitted `.csv` from its `.gz`
file, verifying equality if raw CSV already exists. Run:

```sh
python audit_disease_count_ensemble.py protocol.json EXTRACTED_ROOT \
  retained-first-audit.json EXTRACTED_ROOT/combined_corrected NEW_OUTPUT \
  --continuation EXTRACTED_ROOT/combined-remaining-003 \
  --interrupted-ledger combined-interrupted-ledger.json
```

Keep the two auditor scripts together. The original run-directory names are
validated explicitly, independently from the model variant. Full coverage still
requires exactly ordered indices 0–99. The first seed's source, binary, output
hashes, and published audit are rechecked. Both remaining intervals undergo full
trajectory audits, followed by disease-pool and predicate reconstruction.

All 100 runs end with zero infected survivors, with no extinction. Pool size is
25, maximum disease length is 10, and distinct pool entries range from 19 to 25.
The correction changes both pool count and maximum length; it does not isolate
a causal effect of count. This is a corrected-source sensitivity, not whole-paper
replication credit.
