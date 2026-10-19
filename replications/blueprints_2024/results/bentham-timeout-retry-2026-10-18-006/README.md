# Final two completed local retry inputs

Original Bentham inputs 232 and 237 each complete 5,000 steps and 5,001 audited observations. Final populations are 1273 and 1353.

The exact union reaches **1,841/2,000 homogeneous inputs**, including Bentham **341/500**. The remaining 159 Bentham inputs and other paper experiments remain incomplete.

The local retry supervisor exited at its 2 GiB disk-space guard. Fourteen inputs completed; seven never started. Input 237 finished during executor shutdown: its native completion ledger and full audit establish completion despite its absence from the supervisor ledger. No batch was restarted.

Every archived file matches the retained native evidence. Both full audits reproduce byte-identically after extraction, using the recorded-root option. Commands, coverage, and the terminal observation are retained beside this report.
