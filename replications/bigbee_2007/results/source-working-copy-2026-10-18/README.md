# Google Code working-copy source audit

The [official archived source ZIP](https://storage.googleapis.com/google-code-archive-source/v2/code.google.com/mason-sugarscape/source-archive.zip) contains 870 entries and is 37,100,735 bytes. SHA-256: `a38f7ab88870569c4f2522df1ffa532c6f2cebd28800e4730b393dd1a7b92270`.

Its Subversion working-copy format is version 10, at revision 24. Directory last-change dates span September 28 through October 24, 2011. These dates describe repository changes, not original authorship or experiment dates. The archive contains trunk and branch `amit100`, with no model release under tags. It is a working-copy snapshot, not the complete revision history.

`Agent.java`, `Reproduction.java`, and `Sugarscape.java` match byte-for-byte between trunk and the branch. Agent and reproduction sources match the recovered 2007 release 1.1.2 after newline normalization. `Sugarscape.java` differs. The included LatestNews page explicitly identifies its bundled framework as MASON 16.

Every archive member has a recorded SHA-256. The retained subset preserves all Subversion entries files, the three compared source files from both trees, and the README/news files. Its members were read back and verified against the full ZIP.

This archive does not authenticate the paper's MASON 10 model revision. Its contents do not justify another run of the known faulty reproduction rules or new completion credit. Earlier release 1/1.1.1 bytes remain a source-recovery target; their absence from this snapshot does not prove they are unavailable elsewhere.
