# Two complete Bentham runtime inputs

Original Bentham inputs [0,2) each complete 50,000 steps. The independent audit
validates all 100,002 observations, source/configuration hashes, original seeds,
native command paths, exit records and trajectory hashes. Both terminal
populations fall in the released plotter’s better-or-equal category.

Exact original-input reconciliation reaches **863/1,200 deposited runtime inputs
and 2,549,643 observations**. These two inputs do not overlap earlier evidence.
The remaining 337 deposited inputs and other paper experiments remain required.
The producer was still running when this sealed checkpoint was collected.
This evidence does not resolve the paper’s separate 500-seed runtime claim.

The public archive matches the checksum-verified download, SHA-256
`a6def6bf0507a3181cc9abc00562c58455dc822a63be55cad9c3834fb3207d79`.
Storage receipts identify the original sealed object. After extraction, use:

```sh
python audit_runtime.py ORIGINAL_RUNTIME_ZIP EXTRACTED/benthamHalfLookaheadBinary-50000 NEW_AUDIT --allow-prefix --recorded-root /root/sugarscape/blueprints-bentham50k-memory-001/runs-corrected/benthamHalfLookaheadBinary-50000
```

`audit-command.json` retains the exact executed local command.
