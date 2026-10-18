# Third runtime continuation checkpoint

All eight prefix inputs pass the native runtime audit. Seven overlap the preceding checkpoint exactly, including trajectory hashes; one new input adds 50,001 observations. Coverage is now 881 of 1,200 deposited runtime inputs and 3,001,161 observations. The 50,000-step raw group remains incomplete.

The complete 57.9 MiB native archive is retained locally and in the task-owned object store named by `export-intent.json`. Export status verifies its byte count; local download matches the recorded SHA-256. Member hashes and the full independent audit are retained here. Earlier raw checkpoints remain in prior result folders. This checkpoint does not reproduce the paper’s 500-seed Table 6.
