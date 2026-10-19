# Historical abctools source check

CRAN archive version 1.1.3 predates the 2021 paper; the installed version is 1.1.8, dated July 2025.
Archive bytes and SHA-256 hashes are pinned in `receipts.json`.

`compare.py` reads both downloaded source archives and asserts that `semiauto.abc.R` differs in exactly one expression.
The transformation validation changes `class(te)=="try-error"` to `is(te,"try-error")`.
Sampling, regression, and estimator calculations in this function are unchanged.
The author wrapper supplies transformations, so this validation path is relevant; historical R semantics still require care.
Two other package files differ, as listed in `comparison.json`.

A separate R process confirms that the installed function body and formal arguments match the downloaded 1.1.8 source.
See `installed-source-check.txt` for its assertion result and package/runtime versions.
The live estimator worker and its installed packages were not modified.

This is source evidence, not a historical runtime replay or numerical equivalence test.
It does not resolve dependency versions, random streams, or the 37 discrepant published scores.
No primary result or study completion credit changes.

Reproduce the archive comparison by placing the two files named in `receipts.json` beside `compare.py`, then running `python compare.py`.
Sources: [CRAN archive](https://cran.r-project.org/src/contrib/Archive/abctools/) and [current source](https://cran.r-project.org/src/contrib/abctools_1.1.8.tar.gz).
