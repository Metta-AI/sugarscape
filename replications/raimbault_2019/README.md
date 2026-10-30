# Raimbault et al. (2019): Space Matters

Incomplete paper replication. All 55,000 reference runs reproduce 110,000 archived Gini measurements exactly. The 8,000 generated-input batch also matches Gini; the full generated-landscape experiment remains incomplete.

Sources: [publication 1](https://www.jasss.org/22/4/10.html), [publication 2](https://doi.org/10.7910/DVN/9JI57U).

## Retained workflow

Retains checked source-data download, archived-data analysis, and native reference/generated replay entrypoints with their Java adapters. Sizing probes and checkpoint auditors are archived.

Author code is JusteRaimbault/SpaceMatters revision `270cc7f112b3a999b10e02b0f9525038d6d4754d`. Source data are CC0-1.0; the embedded model carries CC BY-NC-SA 3.0.

Use the pinned prerequisites from the archived study. Uppercase arguments denote supplied paths or identifiers; output paths must be new.

```sh
python replications/raimbault_2019/fetch_sources.py --output NEW_DATA
python replications/raimbault_2019/analyze_archive.py NEW_DATA/reference.csv NEW_DATA/generated.csv --output NEW_ANALYSIS
python replications/raimbault_2019/run_reference.py AUTHOR_ENGINE NETLOGO_APP JAVA_HOME REFERENCE_CSV NEW_RUN --start 0 --stop 55000
```

## Historical study and evidence

The [pinned study record](https://github.com/Metta-AI/sugarscape/tree/a8bbdad0aef6f4f8909b4824af3f41cb51beb425/replications/raimbault_2019) retains full campaigns, removed scripts, reference outputs, source revisions, and dependency environments. It also links earlier raw-data archives.

Findings above describe that recorded study. The retained workflow covers the entrypoints listed here. Export historical files outside this checkout; generated diagnostics belong in temporary or explicitly chosen output directories.
