# Source recovery through the study CLI

`fetch_sources.py` downloads the author release and manuscript to a new directory, preserving received bytes and receipts.
Both downloads match their originally pinned byte counts and SHA256 hashes. All six archive members also match individually.
The unchanged license, citation, metadata, model, map, and ODD description are retained.
The downloader does not install runtimes, execute simulations, or claim paper replication.

The newly downloaded model was transferred to the existing owned CPU host and regenerated the frozen ensemble.
All 1,602 files match the existing preparation byte-for-byte, including manifest SHA256 `3633edf2ca2ec1bd59222e15241655c38c7ec0cacffd1948294ed7c69be85c37`.
The complete original `prepare_ensemble.py` hash is verified before use.
This real download-to-preparation check passes without depending on the original source-recovery directory.
Runtime qualification remains a separate prerequisite documented in the study README.
