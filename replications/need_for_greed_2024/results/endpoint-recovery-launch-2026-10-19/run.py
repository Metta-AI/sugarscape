"""Recover only timed-out original controls after their batch is terminal."""

from pathlib import Path
import hashlib
import json
import subprocess
import sys
import time

root = Path(__file__).resolve().parent
plan = json.loads((root / "plan.json").read_text())
protocol_path = Path(plan["original_protocol"])
assert (
    hashlib.sha256(protocol_path.read_bytes()).hexdigest()
    == plan["original_protocol_sha256"]
)
runner = Path(plan["runner"])
assert hashlib.sha256(runner.read_bytes()).hexdigest() == plan["runner_sha256"]
protocol = json.loads(protocol_path.read_text())
original = protocol_path.parent
deadline = time.monotonic() + plan["wait_seconds"]
while not (original / "terminal.json").exists():
    assert time.monotonic() < deadline, (
        "Original batch has not finished; no recovery started"
    )
    time.sleep(10)
terminal = json.loads((original / "terminal.json").read_text())
assert len(terminal["runs"]) == 6
selected = []
for row in protocol["runs"]:
    receipt = json.loads((Path(row["directory"]) / "terminal.json").read_text())
    assert receipt["entry"] == row["entry"]
    assert receipt["exit_code"] in (0, 124)
    if receipt["exit_code"] == 124:
        assert row["level"] == "1.0"
        selected.append(row)
assert 1 <= len(selected) <= plan["max_inputs"]
(root / "selection.json").write_text(json.dumps(selected, indent=2) + "\n")
results = []
for row in selected:
    output = root / (row["level"] + "-" + row["kind"])
    command = [
        sys.executable,
        str(runner),
        protocol["engine"],
        protocol["archive"],
        row["entry"],
        str(output),
        "--seconds",
        str(plan["per_input_seconds"]),
        "--interpreter",
        protocol["interpreter"],
    ]
    process = subprocess.run(command, check=False)
    result = {
        "entry": row["entry"],
        "exit_code": process.returncode,
        "output": str(output),
    }
    results.append(result)
    print(json.dumps(result), flush=True)
(root / "terminal.json").write_text(
    json.dumps(
        {"runs": results, "all_exit_zero": all(x["exit_code"] == 0 for x in results)},
        indent=2,
    )
    + "\n"
)
