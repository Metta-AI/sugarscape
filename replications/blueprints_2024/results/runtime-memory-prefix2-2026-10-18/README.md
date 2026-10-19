# Five more original runtime inputs

This sealed checkpoint validates Raw inputs [55,62) and Altruist inputs [3,6),
including five previously published inputs. Exact overlap reconciliation adds
only five inputs and 100,546 observations: coverage reaches **868/1,200 inputs
and 2,650,189 observations**. Three new inputs end in natural extinction; two
complete 50,000 steps. No surviving trajectory was shortened.

Audits verify the original configurations, seeds, source and runner hashes,
native commands, zero exit records and every trajectory observation. The
public archive's 90 files match the audited extraction byte for byte.
Provider receipts identify the exported object; the producer remains active.

Extract the archive into a fresh directory. For each group, run
`audit_runtime.py ORIGINAL_RUNTIME_ZIP EXTRACTED/GROUP NEW_AUDIT --allow-prefix
--recorded-root /root/sugarscape/blueprints-runtime-memory-001/runs/GROUP`.
`audit-commands.json` records the exact commands used.

The remaining 332 deposited inputs, the paper's 500-seed runtime experiment
and other paper experiments remain incomplete. This is no whole-paper verdict.
