"""Qualify the four external allocators using the retained artifact sources."""

import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import time

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("qualification", type=Path)
parser.add_argument("output", type=Path)
args = parser.parse_args()
root = args.output.resolve()
root.mkdir(parents=True, exist_ok=False)
hashes = json.loads((args.qualification / "effective-source-sha256.json").read_text())
for name, digest in hashes.items():
    assert (
        hashlib.sha256((args.qualification / "source" / name).read_bytes()).hexdigest()
        == digest
    )
shutil.copytree(args.qualification / "source", root / "source")
(root / "effective-source-sha256.json").write_text(json.dumps(hashes, indent=2) + "\n")
source = root / "source/dynasoar"
for name, command in [
    ("gpu", ["nvidia-smi", "-q"]),
    ("compiler", ["nvcc", "--version"]),
    ("boost", ["dpkg-query", "-W", "libboost-dev"]),
]:
    with (root / f"{name}.txt").open("x") as log:
        subprocess.run(
            command, stdout=log, stderr=subprocess.STDOUT, check=True, timeout=30
        )
records = []
for allocator in ["cuda", "bitmap", "mallocmc", "halloc"]:
    binary = root / allocator
    command = [
        "nvcc",
        "-O3",
        "-g",
        "-std=c++11",
        "-lineinfo",
        "--expt-extended-lambda",
        "-gencode",
        "arch=compute_61,code=compute_61",
        "-maxrregcount=64",
        f"-Iexample/configuration/{allocator}",
        "-I.",
        "-DPARAM_SIZE=32",
        "-DPARAM_MAX_OBJ=262144",
        "-Xcudafe",
        "--diag_suppress=1427",
        "example/sugarscape/dynasoar_no_cell/sugarscape.cu",
        "-o",
        str(binary),
    ]
    if allocator == "mallocmc":
        command.append("-Iexample/configuration/mallocmc/mallocMC")
    if allocator == "halloc":
        command.append("-Iexample/configuration/halloc/halloc/src")
    started = time.monotonic()
    with (root / f"{allocator}-build.log").open("x") as log:
        result = subprocess.run(
            command, cwd=source, stdout=log, stderr=subprocess.STDOUT, timeout=600
        )
    records.append(
        dict(
            kind="build",
            allocator=allocator,
            command=command,
            returncode=result.returncode,
            seconds=time.monotonic() - started,
        )
    )
    (root / "records.json").write_text(json.dumps(records, indent=2) + "\n")
    if result.returncode != 0:
        continue
    for repeat in range(2):
        started = time.monotonic()
        with (root / f"{allocator}-run-{repeat}.log").open("x") as log:
            result = subprocess.run(
                [str(binary)],
                cwd=source,
                stdout=log,
                stderr=subprocess.STDOUT,
                timeout=300,
            )
        records.append(
            dict(
                kind="execution",
                allocator=allocator,
                repeat=repeat,
                returncode=result.returncode,
                seconds=time.monotonic() - started,
                binary_sha256=hashlib.sha256(binary.read_bytes()).hexdigest(),
            )
        )
        (root / "records.json").write_text(json.dumps(records, indent=2) + "\n")
for name, digest in hashes.items():
    assert hashlib.sha256((root / "source" / name).read_bytes()).hexdigest() == digest
(root / "attempt.json").write_text(
    json.dumps(
        dict(
            builds=4,
            executions=sum(r["kind"] == "execution" for r in records),
            scope="Unchanged external allocator adapters. Retain compilation failures before any portability changes. Qualification only; no paper verdict.",
        ),
        indent=2,
    )
    + "\n"
)
assert len(records) == 12 and all(r["returncode"] == 0 for r in records), records
