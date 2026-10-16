"""Execute all 600 declared group-without-policy runs from frozen sources."""

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("engine", type=Path)
parser.add_argument("library", type=Path)
parser.add_argument("output", type=Path)
args = parser.parse_args()
out = args.output.resolve()
out.mkdir(parents=True, exist_ok=False)
root = Path(__file__).resolve().parent
sources = ["run.py", "run_groups.py", "run_phase2.py", "PHASE2_PROTOCOL.md"]
for name in sources:
    shutil.copy2(root / name, out / name)
manifest = {
    "required_runs": 600,
    "seeds": list(range(100)),
    "approaches": ["explicit", "network"],
    "thresholds": [1, 5, 10],
    "policy": "none",
    "steps": 1000,
    "source_sha256": {
        name: hashlib.sha256((out / name).read_bytes()).hexdigest() for name in sources
    },
}
(out / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
with (out / "completed.jsonl").open("x") as ledger:
    for seed in manifest["seeds"]:
        for threshold in manifest["thresholds"]:
            for approach in manifest["approaches"]:
                assert shutil.disk_usage(out).free > 2 * 1024**3, "Less than 2 GiB free"
                name = f"{approach}-{threshold}-{seed}"
                target = out / name
                command = [
                    sys.executable,
                    str(out / "run_groups.py"),
                    str(args.engine.resolve()),
                    str(args.library.resolve()),
                    approach,
                    str(threshold),
                    "none",
                    str(seed),
                    str(target),
                ]
                with (
                    (out / f"{name}.stdout").open("x") as stdout,
                    (out / f"{name}.stderr").open("x") as stderr,
                ):
                    result = subprocess.run(
                        command,
                        check=False,
                        stdout=stdout,
                        stderr=stderr,
                        env={
                            **os.environ,
                            "PYTHONHASHSEED": "0",
                            "PYTHONDONTWRITEBYTECODE": "1",
                        },
                    )
                (out / f"{name}.exit.json").write_text(
                    json.dumps({"exit_code": result.returncode}) + "\n"
                )
                assert result.returncode == 0, f"Failed {name}; retain partial evidence"
                completion = json.loads((target / "run/complete.json").read_text())
                assert completion["steps"] == 1000
                assert (
                    json.loads((target / "parameterization-complete.json").read_text())[
                        "grouping_calls"
                    ]
                    == 1000
                )
                hashes = {
                    str(path.relative_to(target)): hashlib.sha256(
                        path.read_bytes()
                    ).hexdigest()
                    for path in sorted(target.rglob("*"))
                    if path.is_file()
                }
                ledger.write(
                    json.dumps(
                        {
                            "approach": approach,
                            "threshold": threshold,
                            "seed": seed,
                            "command": command,
                            "exit_code": result.returncode,
                            "completion": completion,
                            "sha256": hashes,
                        }
                    )
                    + "\n"
                )
                ledger.flush()
                print(f"Completed {name}", flush=True)
(out / "complete.json").write_text(json.dumps({"completed_runs": 600}) + "\n")
