"""Run full-size native-default timing for the three qualified implementations."""

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import time

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("qualification", type=Path)
parser.add_argument("output", type=Path)
args = parser.parse_args()
source = args.qualification / "source/dynasoar"
hashes = json.loads((args.qualification / "effective-source-sha256.json").read_text())
for name, digest in hashes.items():
    assert (
        hashlib.sha256((args.qualification / "source" / name).read_bytes()).hexdigest()
        == digest
    )
assert json.loads((args.qualification / "complete.json").read_text())["executions"] == 6
root = args.output.resolve()
root.mkdir(parents=True, exist_ok=False)
(root / "effective-source-sha256.json").write_text(json.dumps(hashes, indent=2) + "\n")
for name, command in [
    ("gpu", ["nvidia-smi", "-q"]),
    ("compiler", ["nvcc", "--version"]),
]:
    with (root / f"{name}.txt").open("x") as log:
        subprocess.run(
            command, stdout=log, stderr=subprocess.STDOUT, check=True, timeout=30
        )
records = []
for variant, mode, repeats in [
    ("dynasoar_no_cell", "debug", 1),
    ("dynasoar_no_cell", "release", 5),
    ("baseline_aos", "release", 5),
    ("baseline_soa", "release", 5),
]:
    label = f"{variant}-{mode}"
    binary = root / label
    command = [
        "nvcc",
        "-O3",
        "-g" if mode == "debug" else "-DNDEBUG",
        "-std=c++11",
        "-lineinfo",
        "--expt-extended-lambda",
        "-gencode",
        "arch=compute_61,code=compute_61",
        "-maxrregcount=64",
        "-Iexample/configuration/dynasoar",
        "-I.",
        "-Xcudafe",
        "--diag_suppress=1427",
        f"example/sugarscape/{variant}/sugarscape.cu",
        "-o",
        str(binary),
    ]
    started = time.monotonic()
    with (root / f"{label}-build.log").open("x") as log:
        result = subprocess.run(
            command, cwd=source, stdout=log, stderr=subprocess.STDOUT, timeout=600
        )
    records.append(
        dict(
            kind="build",
            variant=variant,
            mode=mode,
            command=command,
            returncode=result.returncode,
            seconds=time.monotonic() - started,
        )
    )
    (root / "records.json").write_text(json.dumps(records, indent=2) + "\n")
    assert result.returncode == 0
    for repeat in range(repeats):
        started = time.monotonic()
        with (root / f"{label}-run-{repeat}.log").open("x") as log:
            result = subprocess.run(
                [str(binary)],
                cwd=source,
                stdout=log,
                stderr=subprocess.STDOUT,
                timeout=600,
            )
        records.append(
            dict(
                kind="execution",
                variant=variant,
                mode=mode,
                repeat=repeat,
                returncode=result.returncode,
                seconds=time.monotonic() - started,
                binary_sha256=hashlib.sha256(binary.read_bytes()).hexdigest(),
            )
        )
        (root / "records.json").write_text(json.dumps(records, indent=2) + "\n")
        assert result.returncode == 0
for name, digest in hashes.items():
    assert (
        hashlib.sha256((args.qualification / "source" / name).read_bytes()).hexdigest()
        == digest
    )
assert len(records) == 20
(root / "complete.json").write_text(
    json.dumps(
        dict(
            builds=4,
            debug_executions=1,
            release_executions=15,
            grid_side=1700,
            iterations=10000,
            seed=42,
            scope="Native-default contemporary-hardware timings for three implementations. Not matched-heap capacity, independent state validation, or all-allocator replication.",
        ),
        indent=2,
    )
    + "\n"
)
