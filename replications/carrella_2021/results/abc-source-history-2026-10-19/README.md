# Historical abc source comparison

CRAN lists `abc` 2.1 from May 2015 and the next archived release, 2.2.1, from May 2022.
The installed 2.2.2 source dates to December 2024. Version 2.1 is a plausible pre-paper source, not an established author pin.
Downloaded archives, URLs, sizes, and hashes are recorded in `receipts.json`; archive bytes remain external.

Six of eight R source files are byte-identical. Changes occur only in `abc.R` and `cv4postpr.R`.
Parsing `abc.R` in separate R environments shows identical bodies and formal arguments for the estimator `abc` and numerical `summary.abc`.
The only changed function in that file is `hist.abc`, correcting the `unadj=TRUE` histogram path.
The installed estimator and summary functions match the downloaded 2.2.2 source.
The other changed file forwards extra arguments in model-choice cross-validation.

The pinned author `setup.R` calls `abc::abc` and numerical `summary` in its direct estimation branch.
Its semiautomatic branch disables plotting and summarizes `post.sample` directly.
It calls neither histogram plotting nor `cv4postpr`.
These source changes therefore do not explain the observed estimator-score differences along the audited wrapper paths.
Transitive packages, R semantics, numerical libraries, and unknown historical random streams remain unresolved.

The initial comparison guard incorrectly expected `summary.abc` to be the changed function and failed.
Direct function comparison identified `hist.abc`; the final guard asserts that exact name. Both the failed guard and corrected evidence are retained.
No packages were installed or changed, and no primary score or completion status changes.

To repeat, obtain the two pinned archives, extract each `abc/R/abc.R` as `abc-2.1.R` and `abc-2.2.2.R`, then run `Rscript --vanilla check.R DIRECTORY`.
The check requires the recorded installed `abc` 2.2.2 and `jsonlite` packages.
Sources: [CRAN archive](https://cran.r-project.org/src/contrib/Archive/abc/) and [2.2.2 source](https://cran.r-project.org/src/contrib/abc_2.2.2.tar.gz).
