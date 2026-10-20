# Cloud timing qualification

All 48 native qualification inputs match their local references on every non-timing field, including survivor-state hashes. Fresh local replay passes.

The host reports AMD EPYC 9R45 and Temurin Java 11.0.32.1. Execution uses one pinned logical CPU within an eight-core container quota. Host contention is not excluded. This is not the historical paper hardware or runtime.

The passive local benchmark watcher was stopped before admission. Cloud command `cmd-wk4xz` runs the unchanged frozen sequence: 600 warmups and 18,039 measured inputs across six widths. Its outer bound is 12,000 seconds plus 30 seconds termination grace. No automatic retry is authorized.

The CPU8 reservation is $4 at $0.012/minute; the earlier canceled CPU2 reservation remains held pending cost reconciliation. Total continuation reservations are $54 of $100. Reservations are not actual spend.

Benchmark results, held-out frontier transfer, and final study synthesis remain pending. Qualification timings are not benchmark estimates. No completed-study credit is added.

Reproduce the complete qualification audit from this directory:

```sh
python audit_qualification.py .
```

`payload/payload-sha256.json` records the full executed payload. This evidence subset retains every reference and native qualification output used by the audit; it omits runtime JARs and model copies already pinned by the payload receipt.
