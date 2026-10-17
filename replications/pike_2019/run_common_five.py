"""Execute the declared 200-condition threshold-five common-resource grid."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("engine", type=Path)
parser.add_argument("library", type=Path)
parser.add_argument("output", type=Path)
parser.add_argument("--start-index", type=int, default=0)
parser.add_argument("--stop-index", type=int, default=200)
args = parser.parse_args()
assert 0 <= args.start_index < args.stop_index <= 200
out = args.output.resolve()
out.mkdir(parents=True, exist_ok=False)
source = Path(__file__).resolve().parent
names = [
    "run.py",
    "run_common_threshold.py",
    "run_common_five.py",
    "COMMON_THRESHOLD_PROTOCOL.md",
]
for name in names:
    shutil.copyfile(source / name, out / name)
manifest = {
    "required_runs": 200,
    "requested_interval": [args.start_index, args.stop_index],
    "seeds": list(range(100)),
    "threshold": 5,
    "variants": ["common-one", "common-multi"],
    "steps": 1000,
    "source_sha256": {
        n: hashlib.sha256((out / n).read_bytes()).hexdigest() for n in names
    },
}
(out / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
with (out / "completed.jsonl").open("x") as ledger:
    for ordinal in range(args.start_index, args.stop_index):
        seed, variant_index = divmod(ordinal, 2)
        variant = manifest["variants"][variant_index]
        assert shutil.disk_usage(out).free > 8 * 1024**3
        stem = f"{variant}-{seed}"
        destination = out / stem
        command = [
            sys.executable,
            str(out / "run_common_threshold.py"),
            str(args.engine.resolve()),
            str(args.library.resolve()),
            variant,
            "5",
            str(seed),
            str(destination),
        ]
        with (out / (stem + ".log")).open("x") as log:
            result = subprocess.run(
                command,
                stdout=log,
                stderr=subprocess.STDOUT,
                env=os.environ
                | {"PYTHONHASHSEED": "0", "PYTHONDONTWRITEBYTECODE": "1"},
                timeout=240,
            )
        (out / (stem + ".exit.json")).write_text(
            json.dumps({"exit_code": result.returncode}) + "\n"
        )
        assert result.returncode == 0
        assert json.loads(
            (destination / "parameterization-complete.json").read_text()
        ) == {"grouping_calls": 1000}
        completion = json.loads((destination / "run/complete.json").read_text())
        assert completion["steps"] == 1000
        hashes = {
            str(p.relative_to(destination)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(destination.rglob("*"))
            if p.is_file()
        }
        ledger.write(
            json.dumps(
                {
                    "variant": variant,
                    "seed": seed,
                    "threshold": 5,
                    "command": command,
                    "exit_code": result.returncode,
                    "completion": completion,
                    "sha256": hashes,
                }
            )
            + "\n"
        )
        ledger.flush()
        print(f"Completed {variant} seed {seed}", flush=True)
(out / "complete.json").write_text(
    json.dumps({"completed_runs": args.stop_index - args.start_index}) + "\n"
)
