# Durable EC/SARSA evidence

Uploaded the 50-input archive and manifest to `s3://relh-sugarscape-evidence-20261017/brearcliffe-durable-evidence-004/`.
Fresh storage downloads into a new local directory verify the manifest, archive, and all 502 member hashes. This uses storage download readback, not a node-import job.

The 33,543,797-byte archive has SHA-256 `564b55e7d353a588afb8cfc5f76f36e73afa7f4c02863fd28014b0f3fc202910`.
The manifest SHA-256 is `8facb2b02e927ed5e38aeddc14c106f4d1fff33daa0d7228623eddf0003ea145`.

These 50 inputs are disjoint from the prior 353. Four retained backup manifests now cover all 403 audited inputs. Existing trajectory audits are preserved; backup verification adds no simulation or paper-completion credit.
