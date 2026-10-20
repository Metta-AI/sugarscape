# Passive timing recorder qualification

Table 2 reports 50, 88, 173, 427, 1,375, and 3,900 simulations for widths 50, 40, 30, 20, 10, and 5.
Their reported batch times range from 8.48 to 8.53 seconds.
Source: https://www.jasss.org/17/2/6.html, section 4.25 and Table 2.

The existing recorder times setup, 50 ticks, final reporters, survivor hashing, and result construction together.
The separate `RunPolicyTiming` recorder additionally measures setup, simulation steps, and process CPU time before final reporters and export.
Native command compilation and dispatch remain inside these timing intervals; the instrumentation is not a pure NetLogo-kernel timer.
The production evaluator and model are unchanged.

Across all six grid widths, four constant tax rates and two seeds produce 48 paired complete native inputs.
All non-timing outputs, including survivor-state hashes, match exactly across 96 executions.
A corrupted tax outcome is rejected. Fresh archive extraction and re-audit reproduce the audit byte-for-byte.
These runs qualify passive instrumentation; their contended timing values are not benchmark evidence.

The prospective benchmark uses all published batch sizes, three repetitions each, and 100 warmup runs per grid width.
This totals 18,039 measured runs and 600 warmups. The fixed policy has rate 0.25 in all 200 entries, phase zero, and unclipped payments.
Control choice, warmup, seeds, order, and repetition count are declared reconstructions; historical benchmark settings are unavailable.
Both setup-inclusive and step-only estimates will be reported alongside process CPU time.
Throughput-derived equivalent counts will be labeled estimates, separately from actually executed batch counts.

The bounded benchmark waits for this task's existing heavy local jobs to terminate.
This does not guarantee machine-wide idleness; host metadata and load averages will be retained.
Hardware and runtime differ from the historical experiment. No timing-equivalence or completed-study verdict is claimed.
The benchmark has not run, and no new cloud spending is reserved.

To re-audit, extract `native-evidence.tar.gz`, copy `protocol.json` beside the extracted width directories, then run:
`python audit_qualification.py EXTRACTED NEW_AUDIT_JSON`.
Native commands, runtime manifests, hashes, and prospective benchmark controllers are retained for reproduction.
Filesystem paths must be relocated explicitly when reproducing on another machine.
