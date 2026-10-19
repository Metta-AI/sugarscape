# Independent bootstrap-forest fold 2

The second completed fold matches the original seed-zero partition exactly: 4,000 training rows and 1,000 held-out rows. All 755,000 input cells and 5,000 predictions are validated. Prediction error, interval coverage, and interval widths reconstruct within 1e-10.

The auditor selects positions 1,001–2,000 from the original seed-zero permutation. Independent simulation input hashes pass their provenance manifest before analysis. Every native archive member passes hash readback; reauditing the extracted fold reproduces the audit and prediction CSV byte-for-byte.

The saved raw fold, audit source and command, predictions, input provenance, continuation protocol, runner, and R runtime inventory are retained. The unchanged bounded producer continues remaining folds from its saved random state.

Two of five folds are audited: 10,000 held-out predictions and 1,510,000 input-cell checks. Three folds remain. These partial results do not establish the aggregate Table 8 score or complete the paper.
