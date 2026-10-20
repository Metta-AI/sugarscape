# Durable EC/Q evidence

A fresh object-storage import verifies all 502 files in the 33,423,465-byte EC/Q archive. The archive contains 50 previously audited inputs and is disjoint from the prior 303-input backups. Combined durable coverage is 353 audited inputs.

`manifest.json` pins each archive member, input identity, source audit, and preceding backup manifest. Upload receipts, completed import `imp-wsyma`, the exact verifier, and its successful terminal receipt are retained. The import used a new directory on the existing compute node; verification reads the imported archive rather than the producer's original files.

No simulation was repeated and no new completion credit is claimed. This preserves the scientific evidence supporting the separate EC/Q cohort audit.
