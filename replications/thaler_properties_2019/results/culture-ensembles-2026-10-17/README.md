# Complete culture cohort

These archives preserve indices 0–32 from the bounded local runs and 33–99
from the native continuation. The original manifests and complete ledgers remain
unchanged. A timed-out partial index 33 is not included or counted.

Extract each archive into a separate directory. Restore each omitted `.csv`
from its adjacent `.csv.gz`; verify equality when both exist. Run
`audit_observer_ensemble.py RUN PROTOCOL culture OUTPUT` for each variant and
segment. Use `--allow-prefix` for retained runs and `--interval 33 100` for
continuations. Use `original-protocol.json` and `continuation-protocol.json`,
respectively. Name output directories `{variant}-{segment}-audit-001`.

Then run `merge_culture_audits.py original-protocol.json continuation-protocol.json
AUDITS OUTPUT.json`. The merger checks protocol equivalence for model inputs,
pinned retained ledgers, exact seed coverage, and each source-record hash.
Its inputs are outputs of the full trajectory auditor, not substitutes for it.

`files-sha256.json` pins the original evidence package. `readback-validation.json`
records the subsequent archive audit. The merged report includes exact binomial
confidence intervals and all 200 per-seed records. Spatial hill dominance remains
unresolved; corrected-source results are sensitivity analyses.
