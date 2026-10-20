"""Run six bounded, full-horizon native endpoint controls without changing rules."""

from pathlib import Path
import hashlib
import json
import os
import subprocess
import time

root = Path(__file__).resolve().parent
protocol = json.loads((root / "protocol.json").read_text())
assert not (root / "terminal.json").exists()
engine = Path(protocol["engine"])
assert {
    p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in engine.glob("*.py")
} == protocol["source"]["source_sha256"]
results = []
for row in protocol["runs"]:
    directory = Path(row["directory"])
    assert not (directory / "trajectory.json").exists()
    assert (
        hashlib.sha256((directory / "config.json").read_bytes()).hexdigest()
        == row["effective_sha256"]
    )
    command = [
        "/opt/homebrew/bin/timeout",
        "--kill-after=10s",
        "600s",
        protocol["interpreter"],
        str(engine / "sugarscape.py"),
        "--conf",
        str(directory / "config.json"),
    ]
    started = time.monotonic()
    with (
        (directory / "stdout.log").open("x") as stdout,
        (directory / "stderr.log").open("x") as stderr,
    ):
        process = subprocess.run(
            command,
            cwd=engine,
            env={**os.environ, "PYTHONHASHSEED": "0", "PYTHONDONTWRITEBYTECODE": "1"},
            stdout=stdout,
            stderr=stderr,
        )
    receipt = {
        "entry": row["entry"],
        "command": command,
        "exit_code": process.returncode,
        "elapsed_seconds": time.monotonic() - started,
    }
    (directory / "terminal.json").write_text(json.dumps(receipt, indent=2) + "\n")
    results.append(receipt)
    print(json.dumps(receipt), flush=True)
(root / "terminal.json").write_text(
    json.dumps(
        {"runs": results, "all_exit_zero": all(r["exit_code"] == 0 for r in results)},
        indent=2,
    )
    + "\n"
)
