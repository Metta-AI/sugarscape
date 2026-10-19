"""Run the predeclared disjoint seed extension with a wall and storage bound."""

import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import time

root = Path("/Users/relh/Code/workspace")
out = Path(__file__).resolve().parent
protocol = json.loads((out / "protocol.json").read_text())
for name, expected in protocol["input_sha256"].items():
    assert hashlib.sha256(Path(name).read_bytes()).hexdigest() == expected
assert shutil.disk_usage(out).free > 2 * 1024**3
(out / "independent").mkdir()
classpath = (
    str(out) + ":" + str(root / "sugarscape-replication-tools/NetLogo 6.1.1/app/*")
)
commands = [
    (
        "native",
        [
            "/opt/homebrew/opt/openjdk@11/bin/java",
            "-Xmx1g",
            "-Djava.awt.headless=true",
            "-cp",
            classpath,
            "Replay",
            str(
                root
                / "sugarscape-nofreelunch-reference/data/sugarscape/Sugarscape trade.nlogo"
            ),
            str(out / "parameters.csv"),
            "64",
            "576",
            str(out / "native"),
        ],
    )
]
for seed in protocol["fresh_seeds"]:
    commands.append(
        (
            f"independent-{seed}",
            [
                str(root / "sugarscape-replications/.venv/bin/python"),
                str(out / "model.py"),
                str(out / "independent-parameters" / f"{seed}.json"),
                str(out / "independent" / f"row-{seed}.csv"),
            ],
        )
    )
(out / "commands.json").write_text(json.dumps(commands, indent=2) + "\n")
started = time.monotonic()
with (out / "completed.jsonl").open("x") as ledger:
    for name, command in commands:
        assert shutil.disk_usage(out).free > 2 * 1024**3
        remaining = protocol["wall_limit_seconds"] - (time.monotonic() - started)
        assert remaining > 0
        before = time.monotonic()
        with (out / f"{name}.log").open("x") as log:
            result = subprocess.run(
                command, stdout=log, stderr=subprocess.STDOUT, timeout=remaining
            )
        receipt = {
            "name": name,
            "exit_code": result.returncode,
            "elapsed_seconds": time.monotonic() - before,
        }
        ledger.write(json.dumps(receipt) + "\n")
        ledger.flush()
        print(json.dumps(receipt), flush=True)
        assert result.returncode == 0
        assert (
            sum(p.stat().st_size for p in out.rglob("*") if p.is_file())
            < protocol["maximum_outputs_bytes"]
        )
(out / "complete.json").write_text(
    json.dumps({"native_runs": 512, "independent_runs": 512, "exit_code": 0}) + "\n"
)
