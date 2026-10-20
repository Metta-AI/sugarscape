# Remaining original-input inventory

All 10,500 deposited configurations are partitioned without overlap:

| Input class | Audited | Reserved controls | Remaining |
| --- | ---: | ---: | ---: |
| Baseline | 64 | 3 | 333 |
| Selfishness sweep | 100 | 3 | 9,997 |

Every condition contains the same 100 original seeds. Configuration hashes, original field precedence, and full 5,000-step horizons are preserved. Six control inputs remain reserved regardless of interim completion; terminal results must be audited before their disposition changes.

The 333 baseline inputs have prior retained audit reports. Their raw evidence should be recovered before scheduling reruns. This inventory is not a blanket instruction to rerun them. The four additional Blueprint sweep controls use seeds outside this paper’s archive; they add no reusable inputs.

## Measured planning estimate

The 100 verified selfishness-0.37 run receipts have mean elapsed time 518.97 seconds, median 528.29 seconds, and range 1.65–725.92 seconds. Extrapolating that mean to 10,330 inputs across eight workers gives 186.15 hours and $134.03 at the historical $0.012/minute node rate.

This is a single-condition extrapolation on prior shared hardware. Other conditions, CPU capacity, failure rates, and evidence recovery can change it. It excludes setup, export, idle time, and retries; it is not a spending cap or a current provider quote. No node or batch has been launched by this plan.

Before execution, establish a qualified available runtime, aggregate spending bound, per-input timeouts, durable checkpoints, and duplicate-admission checks against active reservations. Existing running experiments keep their original limits.

`prepare.py WORKSPACE NEW_OUTPUT` reads the deposited ZIP, existing audits, six-input control protocol, and hash-verified timing receipts. Two preparations produce byte-identical plan, timing, and compressed input files. `validation.json` records independent inventory counts and checks against the latest retained Blueprints coverage.
