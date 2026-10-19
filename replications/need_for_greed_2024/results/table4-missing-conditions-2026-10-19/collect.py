"""Attach bounded durable collection to the single accepted batch command."""

from pathlib import Path
import json
import subprocess
import time

root = Path(__file__).resolve().parent
deadline = time.monotonic() + 370
while not (root / "submission-retry1.json").exists():
    assert time.monotonic() < deadline, (
        "Launch observation unavailable; never resubmit here"
    )
    time.sleep(5)
receipt = json.loads((root / "submission-retry1.json").read_text())
assert receipt["exit_code"] == 0, receipt
submitted = json.loads(receipt["stdout"])
command = submitted["command_id"]
collector = root.parent / "storage-handoff-20261017-001/collect_storage_api_bounded.py"
with (root / "collector.log").open("x") as stream:
    result = subprocess.run(
        [
            "/Users/relh/Code/workspace/sugarscape-replications/.venv/bin/python",
            str(collector),
            "relh-sugarscape-selfishness037-cpu8-20261018-v1",
            command,
            root.name,
            "--seconds",
            "34200",
            "--max-bytes",
            str(2 * 1024**3),
        ],
        stdout=stream,
        stderr=subprocess.STDOUT,
        timeout=34400,
    )
(root / "collection-terminal.json").write_text(
    json.dumps({"exit_code": result.returncode, "command_id": command}, indent=2) + "\n"
)
assert result.returncode == 0
