# Native training archive qualification

The complete three-epoch pathwise qualification contains 15 native files and 1,615,313 bytes.
The archive builder preserves every audited parameter, gradient, validation draw, observation, and completion file.
It groups at most 500 epochs per archive and rejects archives exceeding 256 MiB.

All three storage objects were uploaded and freshly downloaded.
Their hashes match, and every downloaded archive member matches the original native optimizer audit.
This qualifies the three-epoch archival workflow only. Neither full 5,000-epoch arm has an archive verdict yet.
No new simulations or completed-study credit are added.

The storage prefix is `relh-sugarscape-evidence-20261017/quera-training-archive-qualification-20261020-001/`.
`manifest.json` pins every native member and archive; `qualification.json` records the fresh remote readback.
The original optimizer qualification remains authoritative for method correctness.

After a full arm exits successfully and its optimizer audit passes, seal it with:

```sh
python replications/quera_2025/seal_training.py \
  CAMPAIGN/pathwise CAMPAIGN/pathwise-audit.json CAMPAIGN/pathwise-exit.json \
  5000 NEW_ARCHIVE_DIRECTORY
```

Use the corresponding VarGrad paths for the second arm.
The command requires a new output directory, complete audited membership, and sufficient free space.
It creates and reopens each archive, verifying every member against the native audit.
Upload and fresh remote verification remain separate required steps; local sealing does not claim remote durability.
