# Final bounded runtime checkpoint

The six-hour command `cmd-byham` ended at 01:28:08 UTC on October 18 with exit code one.
Both child groups raised `subprocess.TimeoutExpired` when their remaining wall-clock allowance expired.
The final checkpoint preserves the complete ledgers, both failure logs, and terminal codes `[1,1]`.
A subsequent targeted process check found no workers using the stopped batch's output path.
This is a bounded partial run, not successful completion of either declared interval.

The 54,711,591-byte checkpoint was exported successfully to task-owned object storage.
Its downloaded SHA-256 matches the sealed receipt; extraction contains 269,416,633 bytes.
The independent auditor validates all 33 completed inputs:

| Group | Original indices | Completed inputs | Remaining indices |
| --- | --- | ---: | --- |
| Bentham, 5,000 steps | `[52,80)` | 28 | `[80,100)` |
| Egoistic, 50,000 steps | `[11,16)` | 5 | `[16,100)` |

All 28 overlapping records agree with prior evidence in seed, trajectory hash,
endpoint, observation count and classification. Five newly completed Bentham inputs
add 25,005 observations. Unique deposited-runtime coverage reaches **854/1,200 inputs
and 2,199,311 observations**. Bentham 5,000-step coverage is now 80/100;
egoistic 50,000-step coverage remains 16/100.

The interrupted seeds are 7753991106316778181 for Bentham and 2732067017264549820
for Egoistic. Their incomplete native files remain in the original remote directory
and receive no completion credit. Any continuation must start in a fresh output
directory at the audited remaining index; it must preserve those failed artifacts.

The previously authorized commands `cmd-2ypbn` and `cmd-52ges` began their disjoint
Bentham 50,000-step intervals after the prior terminal receipt appeared.
They were verified running; neither was restarted or replaced by this audit.

The two group directories retain frozen manifests, ledgers, runner/source pins
and independent audit reports. These captured execution scripts are unchanged inputs.
`readback.json` identifies the archive, export, failure interpretation and remaining intervals.
`coverage.json` records the complete deduplicated union and every contributing audit hash.
`sha256.json` pins the exported evidence. The raw checkpoint remains externally retained
and in object storage at the recorded location.

Recheck either extracted group with:

```sh
python replications/blueprints_2024/audit_runtime.py ORIGINAL_RUNTIME_ZIP EXTRACTED_GROUP NEW_AUDIT_DIRECTORY --allow-prefix --recorded-root ORIGINAL_REMOTE_GROUP_PATH
```

This covers the deposited 100-input runtime groups. It does not establish the
paper's separate 500-seed timing schedule or complete the study.
