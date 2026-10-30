# Brearcliffe and Crooks: intelligent agents

Completed qualified author-code study. All 1,600 inputs and 32,001,600 observations were audited under both parameter interpretations. Outcomes are mixed; exact historical agreement and a validated negative result are not established.

## Retained workflow

Retains source acquisition, ensemble preparation/assignment, native input/batch execution, Java adapter, and complete-run audit. The 1,729-line figure inventory, digitizers, comparison campaigns, and per-cohort summaries are archived.

Use the pinned prerequisites from the archived study. Uppercase arguments denote supplied paths or identifiers; output paths must be new.

```sh
python replications/brearcliffe_2020/fetch_sources.py NEW_SOURCE_INPUTS
python replications/brearcliffe_2020/prepare_ensemble.py AUTHOR_MODEL NEW_PREPARED
python replications/brearcliffe_2020/run_ensemble_input.py NEW_PREPARED RUN_ID QUALIFIED_RUNTIME_ASSETS NETLOGO_APP NEW_RUN --java JAVA_EXECUTABLE --timeout-seconds 1800
```

## Historical study and evidence

The [pinned study record](https://github.com/Metta-AI/sugarscape/tree/c2dbfba6056051bd36d8bd790990a49907699f70/replications/brearcliffe_2020) retains full campaigns, removed scripts, reference outputs, source revisions, and dependency environments. It also links earlier raw-data archives.

Findings above describe that recorded study. The retained workflow covers the entrypoints listed here. Export historical files outside this checkout; generated diagnostics belong in temporary or explicitly chosen output directories.
