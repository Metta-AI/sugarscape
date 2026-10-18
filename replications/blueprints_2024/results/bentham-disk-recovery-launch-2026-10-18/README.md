# Seven original inputs moved to bounded remote execution

The local supervisor stopped at its disk-space guard. Inputs 254, 255, 269, 288, 292, 301 and 316 had never started there. They are disjoint from the 152-input CPU8 queue; together they cover the 159 remaining original Bentham inputs.

Owned node `relh-sugarscape-bentham-disk-cpu2-20261018-v1` runs command `cmd-x4ner` with two workers. Each input retains its original seed, configuration and 5,000-step horizon. The simulation runners, source auditor, process supervisor and Linux qualification workflow are byte-identical to the existing CPU8 payload. Only allocation and resource checks change.

The batch has a six-hour work limit, two hours per input and a 25,500-second outer deadline. The quoted CPU2 rate is $0.0024/minute: approximately $1.06 including the 15-minute idle window at the maximum duration. The collector allows 100 MiB and 27,000 seconds, exporting terminal evidence to owned storage without waking a stopped node.

The node provisioned before boot-command registration. That registration was rejected without execution; its error is retained. The uploaded script hash was verified before the successful detached launch. No duplicate simulation was launched. The original local failure and all finished evidence remain intact.

This records an active execution, not completed inputs or replication credit. Terminal outputs still require the full source/configuration/trajectory audit and duplicate-free union reconciliation.

## Qualification failure and verified recovery

The first detached command exited 1 during qualification, before any assigned Bentham input. Packaging accidentally replaced the auditor's pinned source manifest with a payload-hash dictionary. The auditor rejected that schema with `KeyError: source_sha256`.

Recovery preserves the failed manifest, original logs and failed qualification directory. It restores the unchanged CPU8 source manifest and reruns all four lifecycle controls. These pass; the completed control reproduces its original trajectory hash exactly. Replacement command `cmd-msyhs` is verified running inputs 254 and 255. The recovery collector is session 49698, storage prefix `blueprints-bentham-disk-recovery-cpu2-002`; the original collector failed because no terminal artifact existed.

`recovery.sh` and hash-verified upload receipts document the correction. The original boot payload remains failed evidence, not a runnable corrected recipe. Apply the retained recovery sequence after that failed bootstrap to reproduce the executed workflow. No study input completed in the failed attempt.
