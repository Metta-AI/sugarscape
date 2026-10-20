# Local analysis interpreter recovery

The task virtual environment disappeared during an active turn; the cause is unknown.
Failed invocations reported exit 127. Remote simulations and existing long-running collectors remained live.
The missing local path was recreated with the same CPython 3.11.14 interpreter.
Pydantic 2.12.5 was installed explicitly; the prior dependency version was not established.

Both complete analysis commands reproduce prior reports byte-for-byte: baseline checkpoint 0010 and Table IV checkpoint 0177.
The commands, report hashes, interpreter identity, and installed dependency versions are retained here.
No simulation was restarted, and no trajectory or completed-study credit follows from environment repair.
