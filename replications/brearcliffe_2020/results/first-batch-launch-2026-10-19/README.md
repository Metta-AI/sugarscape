# First bounded dispatcher execution

The dispatcher admits two previously unstarted released-code inputs from the audited remaining manifest.
Both are Rule M/Rule M repetitions 00 and 01. Neither duplicates the completed Rule M/EC input.
Session17973 owns this local run: two workers,600seconds per input plus30seconds wrapper allowance,900seconds total admission horizon,1GiB Java heap per worker.

The dispatcher validates each selected row against the frozen manifest and records its remaining-manifest hash.
It never overwrites an existing batch directory. After an input failure, it stops admitting more work and allows already-running bounded inputs to finish.
A terminal summary separates successful,failed and unstarted inputs. Independent `audit_ensemble.py` verification is required before any coverage credit.

This exercises the complete public batch workflow on actual full-length ensemble inputs. Results are pending; no completed-input or paper credit is added by this launch.
