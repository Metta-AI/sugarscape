# Pre-submission death-definition history

The author repository adds aging deaths in [v2024.3, August 23, 2024](https://github.com/digital-terraria-lab/sugarscape/commit/cc0408afbb09d8d124ce6f7e6b1844d202d0f8b6). The paper was received October 10, accepted December 12, and published December 17, 2024. These dates make this released definition a historically plausible explanation for Figure 6.

The earlier v2024.1 plotter uses starvation plus combat. v2024.3 computes `(starvation + combat + aging) / population * 100`. v2024.4 retains that formula. Its parser also changes the equality classification boundary and plotting backend, so this finding does not justify substituting a later simulation release.

The retained source expression is checked through Python's syntax tree. Recomputing its formula from the audited native ensemble means matches **all 19,970 published Figure 6 vertices** across four models under the existing 0.005 PDF-point tolerance. Disease deaths are zero at every one of the 5,001 ensemble timesteps for each model, making the historical three-cause formula equivalent to the earlier all-cause comparison here.

| Model | Matching vertices | Maximum PDF-point error |
| --- | ---: | ---: |
| Raw | 4,996 | 0.003699 |
| Altruist | 4,995 | 0.003700 |
| Egoist | 4,992 | 0.003922 |
| Utilitarian | 4,987 | 0.004067 |

This supplies author-released, pre-submission provenance for the matching definition. It does **not** identify the exact historical plotting revision or prove which command the authors executed. The original simulator remains pinned to v2024.1, as specified by the paper. Full-paper replication remains incomplete.

`history.json` records all ten plotting-file revisions reachable from the fetched local refs, including dates, source hashes, and matching source lines. `refs.txt` bounds that inventory; it is not a claim about inaccessible or deleted history. The v2024.1, v2024.3 and v2024.4 plotting sources and introducing patch are retained. `compare.py REPOSITORY OUTPUT` rechecks the source expression, all ensemble timesteps, and every extracted Figure 6 vertex against the previously published evidence.
