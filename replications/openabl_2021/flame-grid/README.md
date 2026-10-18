# Complete published FLAME input grid

All five Figure4 FLAME sizes,250 through4,000 requested cells, execute100 steps using the released model. Independent reconstruction matches60,600 initial fields and60,600 final fields. No buffer or neighbor-order model correction is needed for these conditions.

All505 native XML snapshots are retained. Structural and resource checks cover765,075 agent observations; only endpoint dynamics are independently replayed here. FLAME linked-list traversal changes array order, so endpoint records are compared by fixed coordinates.

Dependencies are pinned to xparser `a6239f90b42beb34352486e638a4332cf83e97fb` and libmboard `5fd34e83b932dcda5bb6c177277b8557fbe01229`. These precede paper acceptance but are not verified author revisions. The library uses the serial configuration specified by OpenABL. GCC16 requires `-fcommon` for tentative globals in generated headers; default generated optimization flags remain unchanged. The earlier41-symbol link failure and missing-template environment error are preserved.

Every archive member matches its retained source byte-for-byte. The raw outputs, generated C, binaries, configuration XML, commands, dependency pins, build failures, and validators are included. This verifies the observed behavior under the reconstructed runtime; historical timings, GPU and distributed scopes remain incomplete.
