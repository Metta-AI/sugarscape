# Paginated evidence collector for the released-code ensemble

The original local collector reads only one command-log page and would reject a truncated response.
The live log has reached 56,369 bytes; its eventual archive receipt can arrive after the first page fills.
The already-qualified paginated collector now follows byte offsets and reassembles complete snapshot lines.

The task-owned old collector was identified by PID and exact command, then stopped before its replacement started.
Its latest receipt recorded zero exported bytes; all previous logs remain retained.
The replacement observes the same running producer `cmd-vxb2x` and preserves the original deadline, 23:22:35 UTC on October 19.
Its admission window is the remaining 12,332 seconds, with the same two-gibibyte artifact cap.
The initial live read succeeded and found no sealed final archive yet.

Only the local evidence collector changed. No simulation was stopped, restarted, or extended, and no new result credit follows.
The independent bounded paper-table ensemble and its collector remain separate.
