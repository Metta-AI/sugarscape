# Baseline collector pagination and bounded input failure

The command log exceeded the provider's 65,536-byte first page. The prior collector rejected truncated output and stopped.
The paginated replacement follows the API's byte offsets, reassembles lines across page boundaries, and retains the existing bounded export workflow.
A live end-to-end check reads both pages, parses 37 complete input receipts, and exports the sealed checkpoint successfully.
The replacement bounds each log read to 8 MiB and retains three bounded retries for transient read failures.
It preserves the old collector failure and starts under a new storage prefix within the previous collector deadline.
No simulation is restarted, and prior exports remain intact.

Pagination exposes one unsuccessful baseline input: `egoisticHalfLookaheadBinary530238075247992587.config`, exit 124 at its existing native time limit.
The coordinator stops new admissions on that failure and allows already-started inputs to finish.
The initial live-pagination check incorrectly required every producer receipt to be successful; that assumption was removed so failures remain visible.
An earlier transient log-read failure was followed by authoritative checks showing both node and command still running.
Neither observation failure caused a restart.

The sealed checkpoint export is 5,178,003 bytes and retains its original SHA-256.
This restores evidence collection; it adds no audited inputs, table results, or completed-paper credit.
The current inventory remains 219 inputs and 1,013,026 observations. Final successful and failed artifacts still require reconciliation.
