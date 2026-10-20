# Market algorithm candidate qualification

[The author-hosted paper](https://jameslcaton.com/MarketAlgorithmAsDistributedGeneticAlgorithm-Johnson%2CCaton%2CMiljkovic%2CRayamajhee.pdf) links directly to [the released Sugarscape implementation](https://github.com/zacharyejohnson/Academics/tree/38089136a115642d3f79416681f530b36d4bf70c/Sugarscape).
Nine source/configuration files were retained locally and verified against Git blob identities and SHA-256 hashes.

The paper specifies 100 repeats per model, 100,000 periods for basic agents, and 60,000 for optimizer and mixed populations.
The current driver instead specifies six repeats, 10,000 basic periods and 5,000 optimizer/mixed periods.
Both initialize 2,000 agents. These released defaults cannot stand in for the paper experiment.

Eleven historical driver versions were inspected. Their literal settings are retained in qualification.json.
The next older path lookup returned HTTP 404; older renamed paths remain unresolved.
The environment is a Windows Conda export, while the model forces TkAgg and the driver uses SQL collection.
Runtime qualification remains outstanding.

GitHub metadata reports MIT, but the license endpoint and root LICENSE return 404.
The complete recursive tree contains no license-named paths. Licensing remains unresolved; author source is not copied into this PR.
The first failed license lookup is retained separately.

No simulations, study PR, or completion credit are claimed. Next steps are notebook/history reconciliation and a bounded native control.

The released analysis notebook is now hash-verified against its Git blob. Its loader references `Sugarscape_Alt -10-25-2023`, absent from the complete pinned tree. Saved output shows 100 rows for each of three model types, but the required basic-only and optimizer-only datasets are absent. The released Parquet directories instead include two arbitrageur variants and a mixed variant. Saved notebook output is not independent reproduction; its source revision and underlying data remain unresolved. The older failed GUI lookup is confirmed as a deletion, not a recovered rename.

[Historical data recovery](../market-genetic-history-2026-10-19) finds deleted basic-only and optimizer-only tables with 30 runs of 5,000 observations each. Their values and stored-precision means pass audit. They do not recover the longer 100-run experiment referenced by the paper.
