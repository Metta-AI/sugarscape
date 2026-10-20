# Complete frozen optimizer campaign

All eighteen searches complete: six grid widths and three optimizer seeds, with 24 candidates, 20 generations, and 50 simulator seeds each.
The campaign evaluates 432,000 native simulations over 360 generations.
Fresh independent replay reproduces all original audits byte-for-byte, including 3,307 matings and 142,998 mutated components.
The final evaluated frontiers contain 144 policies. Unevaluated final children are retained separately and are not reported as evaluated policies.

The archive contains every native search input/output, genetic-decision record, protocol, receipt, audited source model, and audit.
Local archive readback verifies 2,430 members. A fresh storage download matches all members and the full archive hash.

- Object: `relh-sugarscape-evidence-20261017/oremland-search-completion-001/complete-searches.tar.gz`
- Bytes: 47,976,761
- SHA-256: `35823512b1317960d58050c71b51e46a8c55fad86fc2035f85baf917d8571e8f`

```sh
autor storage cp relh-sugarscape-evidence-20261017/oremland-search-completion-001/complete-searches.tar.gz NEW_ARCHIVE.tar.gz
python verify_storage.py NEW_ARCHIVE.tar.gz audit.json NEW_VERIFICATION.json
```

All 144 final policies are scheduled for full-model evaluation on 200 held-out seeds, totaling 28,800 native evaluations.
That transfer campaign is active and is not counted as complete here.
Training objectives across differently sized models are not substituted for full-model transfer objectives.
Historical optimizer budgets and reduction conventions remain unknown; the declared reconstruction choices remain unchanged.
This completes the frozen search workflows, not global optimization, the timing benchmark, or the entire paper replication.
