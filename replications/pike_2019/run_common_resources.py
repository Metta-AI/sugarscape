"""Execute 198 remaining native common-resource conditions with frozen inputs."""

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
args = parser.parse_args()
out = args.output.resolve()
out.mkdir(parents=True, exist_ok=False)
root = Path(__file__).resolve().parent
for name in ["run.py", "COMMON_RESOURCE_PROTOCOL.md", "run_common_resources.py"]:
    shutil.copy2(root / name, out / name)
manifest = {
    "required_runs": 198,
    "complete_grid_including_prior_seed_zero": 200,
    "numpy_seeds": list(range(1, 100)),
    "mesa_seed": 42,
    "variants": ["common-one", "common-multi"],
    "steps": 1000,
    "source_hashes": {
        name: hashlib.sha256((out / name).read_bytes()).hexdigest()
        for name in ["run.py", "COMMON_RESOURCE_PROTOCOL.md", "run_common_resources.py"]
    },
}
(out / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
with (out / "completed.jsonl").open("x") as ledger:
    for seed in range(1, 100):
        for variant in manifest["variants"]:
            assert shutil.disk_usage(out).free > 8 * 1024**3, "Less than 8 GiB free"
            run = out / f"{variant}-{seed}"
            command = [
                sys.executable,
                str(out / "run.py"),
                str(args.engine.resolve()),
                str(args.library.resolve()),
                variant,
                str(seed),
                str(run),
            ]
            with (
                (out / f"{variant}-{seed}.stdout").open("x") as stdout,
                (out / f"{variant}-{seed}.stderr").open("x") as stderr,
            ):
                result = subprocess.run(
                    command,
                    env={
                        **os.environ,
                        "PYTHONHASHSEED": "0",
                        "PYTHONDONTWRITEBYTECODE": "1",
                    },
                    stdout=stdout,
                    stderr=stderr,
                )
            (out / f"{variant}-{seed}.exit.json").write_text(
                json.dumps({"exit_code": result.returncode}) + "\n"
            )
            assert result.returncode == 0, (
                f"Failed {variant} seed {seed}; preserve partial evidence"
            )
            completion = json.loads((run / "complete.json").read_text())
            assert completion["steps"] == 1000
            hashes = {
                p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                for p in sorted(run.iterdir())
                if p.is_file()
            }
            ledger.write(
                json.dumps(
                    {
                        "variant": variant,
                        "numpy_seed": seed,
                        "command": command,
                        "exit_code": result.returncode,
                        "completion": completion,
                        "hashes": hashes,
                    }
                )
                + "\n"
            )
            ledger.flush()
            print(f"Completed {variant} seed {seed}", flush=True)
(out / "complete.json").write_text(json.dumps({"completed_runs": 198}) + "\n")
