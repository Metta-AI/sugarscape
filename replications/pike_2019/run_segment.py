"""Execute a bounded contiguous grid segment using an existing frozen phase manifest."""

import argparse
import hashlib
import json
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path

import mesa
import networkx
import numpy

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("frozen", type=Path)
parser.add_argument("engine", type=Path)
parser.add_argument("library", type=Path)
parser.add_argument("phase", type=int, choices=[1, 2, 3])
parser.add_argument("start", type=int)
parser.add_argument("stop", type=int)
parser.add_argument("output", type=Path)
args = parser.parse_args()
assert (
    platform.python_version(),
    mesa.__version__,
    numpy.__version__,
    networkx.__version__,
) == ("3.11.14", "0.8.5", "1.26.4", "3.6.1"), "The declared Pike runtime is required"
manifest_bytes = (args.frozen / "manifest.json").read_bytes()
manifest = json.loads(manifest_bytes)
required = {1: 300, 2: 600, 3: 1200}[args.phase]
assert manifest["required_runs"] == required and manifest["steps"] == 1000
assert 0 <= args.start < args.stop <= required
source_key = "source_hashes" if args.phase == 1 else "source_sha256"
for name, digest in manifest[source_key].items():
    assert hashlib.sha256((args.frozen / name).read_bytes()).hexdigest() == digest
if args.phase == 1:
    assert manifest["numpy_seeds"] == list(range(100))
    assert manifest["variants"] == ["standard", "explicit", "network"]
    grid = [
        {"numpy_seed": seed, "variant": variant}
        for seed in manifest["numpy_seeds"]
        for variant in manifest["variants"]
    ]
else:
    assert manifest["seeds"] == list(range(100))
    assert manifest["thresholds"] == [1, 5, 10]
    assert manifest["approaches"] == ["explicit", "network"]
    assert manifest["policy"] == ("none" if args.phase == 2 else "movement")
    grid = [
        {"seed": seed, "threshold": threshold, "approach": approach}
        for seed in manifest["seeds"]
        for threshold in manifest["thresholds"]
        for approach in manifest["approaches"]
    ]
    if args.phase == 3:
        assert manifest["selectors"] == ["released", "corrected-highest"]
        grid = [
            {**condition, "selector": selector}
            for condition in grid
            for selector in manifest["selectors"]
        ]
out = args.output.resolve()
out.mkdir(parents=True, exist_ok=False)
for name in manifest[source_key]:
    shutil.copyfile(args.frozen / name, out / name)
(out / "manifest.json").write_bytes(manifest_bytes)
(out / "segment.json").write_text(
    json.dumps(
        {
            "phase": args.phase,
            "ordinal_interval": [args.start, args.stop],
            "manifest_sha256": hashlib.sha256(manifest_bytes).hexdigest(),
            "runner_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            "python": platform.python_version(),
            "platform": platform.platform(),
            "machine": platform.machine(),
        },
        indent=2,
    )
    + "\n"
)
with (out / "completed.jsonl").open("x") as ledger:
    for condition in grid[args.start : args.stop]:
        assert shutil.disk_usage(out).free > 2 * 1024**3, "Less than 2 GiB free"
        if args.phase == 1:
            stem = f"{condition['variant']}-{condition['numpy_seed']}"
            script = "run.py"
            arguments = [condition["variant"], str(condition["numpy_seed"])]
        else:
            stem = (
                f"{condition['approach']}-{condition['threshold']}-{condition['seed']}"
            )
            script = "run_groups.py"
            arguments = [
                condition["approach"],
                str(condition["threshold"]),
                manifest["policy"],
                str(condition["seed"]),
            ]
            if args.phase == 3:
                stem += "-" + condition["selector"]
                if condition["selector"] == "corrected-highest":
                    script = "run_high_focus.py"
                    arguments = [
                        condition["approach"],
                        str(condition["threshold"]),
                        str(condition["seed"]),
                    ]
        target = out / stem
        command = [
            sys.executable,
            str(out / script),
            str(args.engine.resolve()),
            str(args.library.resolve()),
            *arguments,
            str(target),
        ]
        with (
            (out / f"{stem}.stdout").open("x") as stdout,
            (out / f"{stem}.stderr").open("x") as stderr,
        ):
            result = subprocess.run(
                command,
                stdout=stdout,
                stderr=stderr,
                env={
                    **os.environ,
                    "PYTHONHASHSEED": "0",
                    "PYTHONDONTWRITEBYTECODE": "1",
                },
            )
        (out / f"{stem}.exit.json").write_text(
            json.dumps({"exit_code": result.returncode}) + "\n"
        )
        assert result.returncode == 0, f"Failed {stem}; preserve partial evidence"
        configured = target
        if args.phase == 3 and condition["selector"] == "corrected-highest":
            configured = target / "configured"
        completion_path = configured / (
            "complete.json" if args.phase == 1 else "run/complete.json"
        )
        completion = json.loads(completion_path.read_text())
        assert completion["steps"] == 1000
        if args.phase != 1:
            assert (
                json.loads((configured / "parameterization-complete.json").read_text())[
                    "grouping_calls"
                ]
                == 1000
            )
        hashes = {
            str(path.relative_to(target)): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in sorted(target.rglob("*"))
            if path.is_file()
        }
        record = {
            **condition,
            "command": command,
            "exit_code": result.returncode,
            "completion": completion,
            "hashes" if args.phase == 1 else "sha256": hashes,
        }
        ledger.write(json.dumps(record) + "\n")
        ledger.flush()
        print(f"Completed {stem}", flush=True)
(out / "segment-complete.json").write_text(
    json.dumps(
        {
            "ordinal_interval": [args.start, args.stop],
            "completed_runs": args.stop - args.start,
        }
    )
    + "\n"
)
