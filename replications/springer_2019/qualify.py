"""Compile and execute the pinned author artifact on one CUDA GPU."""

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import time
import urllib.request
import zipfile

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("output", type=Path)
parser.add_argument("--cub", choices=["artifact", "toolkit"], required=True)
parser.add_argument(
    "--source-mode", choices=["archived", "portable-syntax"], required=True
)
args = parser.parse_args()
root = args.output.resolve()
root.mkdir(parents=True, exist_ok=False)
url = "https://drops.dagstuhl.de/storage/artifacts/darts-vol005/darts-vol005-issue002_ecoop2019/658/DARTS-5-2-2-artifact-e7b8bb33961ae66209581e2c58c6cad3.zip"
with urllib.request.urlopen(url, timeout=60) as response:
    raw = response.read(10_000_001)
assert len(raw) <= 10_000_000
assert (
    hashlib.sha256(raw).hexdigest()
    == "75421734305809c5999904082616996a904a19a5e43466cf076ec10660e559a1"
)
assert hashlib.md5(raw).hexdigest() == "e7b8bb33961ae66209581e2c58c6cad3"
(root / "artifact.zip").write_bytes(raw)
with zipfile.ZipFile(root / "artifact.zip") as archive:
    for member in archive.infolist():
        assert not Path(member.filename).is_absolute()
        assert ".." not in Path(member.filename).parts
    source_hashes = {
        member.filename: hashlib.sha256(archive.read(member)).hexdigest()
        for member in archive.infolist()
        if not member.is_dir()
    }
    archive.extractall(root / "source")
(root / "source-sha256.json").write_text(json.dumps(source_hashes, indent=2) + "\n")
effective_hashes = source_hashes.copy()
if args.source_mode == "portable-syntax":
    name = "dynasoar/allocator/allocator_handle.h"
    path = root / "source" / name
    original = path.read_text()
    assert original.count("allocator_->parallel_do<") == 4
    corrected = original.replace(
        "allocator_->parallel_do<", "allocator_->template parallel_do<"
    )
    (root / "original-allocator_handle.h").write_text(original)
    path.write_text(corrected)
    effective_hashes[name] = hashlib.sha256(path.read_bytes()).hexdigest()
    (root / "source-change.json").write_text(
        json.dumps(
            {
                "author_fix_commit": "2bede5fc9ec715e13be6a77e12f758a4549c815b",
                "file": name,
                "inserted_template_keywords": 4,
                "original_sha256": source_hashes[name],
                "effective_sha256": effective_hashes[name],
                "scope": "Apply the author's dependent-template syntax correction to four existing calls; no model rules changed.",
            },
            indent=2,
        )
        + "\n"
    )
    name = "dynasoar/bitmap/bitmap.h"
    path = root / "source" / name
    original = path.read_text()
    corrected = original
    for method in ["atomic_add_scan_init", "atomic_add_scan"]:
        old = f"&ThisClass::{method}>"
        assert corrected.count(old) == 1
        corrected = corrected.replace(old, f"&ThisClass::template {method}<S>>")
    (root / "original-bitmap.h").write_text(original)
    path.write_text(corrected)
    effective_hashes[name] = hashlib.sha256(path.read_bytes()).hexdigest()
    (root / "bitmap-source-change.json").write_text(
        json.dumps(
            {
                "file": name,
                "explicit_template_arguments": 2,
                "original_sha256": source_hashes[name],
                "effective_sha256": effective_hashes[name],
                "scope": "Explicitly select the surrounding scan<S> specialization for two member-function pointers; no bitmap algorithm change. This is a local compiler-portability edit, not an authenticated historical source revision.",
            },
            indent=2,
        )
        + "\n"
    )
(root / "effective-source-sha256.json").write_text(
    json.dumps(effective_hashes, indent=2) + "\n"
)
for name in ["cub/version.cuh", "thrust/version.h"]:
    raw = (Path("/usr/local/cuda/include") / name).read_bytes()
    (root / name.replace("/", "-")).write_bytes(raw)
for name, command in [
    ("gpu", ["nvidia-smi", "-q"]),
    ("compiler", ["nvcc", "--version"]),
    ("host-compiler", ["g++", "--version"]),
    ("system", ["uname", "-a"]),
]:
    with (root / f"{name}.txt").open("x") as log:
        subprocess.run(
            command, stdout=log, stderr=subprocess.STDOUT, check=True, timeout=30
        )

records = []
source = root / "source/dynasoar"
for variant in ["dynasoar_no_cell", "baseline_aos", "baseline_soa"]:
    binary = root / variant
    command = [
        "nvcc",
        "-g",
        "-O3",
        "-std=c++11",
        "-lineinfo",
        "--expt-extended-lambda",
        "-gencode",
        "arch=compute_61,code=compute_61",
        "-maxrregcount=64",
        "-Iexample/configuration/dynasoar",
        "-I.",
        "-DPARAM_SIZE=32",
        "-DPARAM_MAX_OBJ=262144",
        "-Xcudafe",
        "--diag_suppress=1427",
        f"example/sugarscape/{variant}/sugarscape.cu",
        "-o",
        str(binary),
    ]
    if args.cub == "artifact":
        command.insert(1, "-Ilib/cub")
    started = time.monotonic()
    with (root / f"{variant}-build.log").open("x") as log:
        result = subprocess.run(
            command, cwd=source, stdout=log, stderr=subprocess.STDOUT, timeout=600
        )
    records.append(
        {
            "kind": "build",
            "variant": variant,
            "command": command,
            "returncode": result.returncode,
            "seconds": time.monotonic() - started,
        }
    )
    (root / "records.json").write_text(json.dumps(records, indent=2) + "\n")
    if result.returncode != 0:
        continue
    for repeat in range(2):
        started = time.monotonic()
        with (root / f"{variant}-run-{repeat}.log").open("x") as log:
            result = subprocess.run(
                [str(binary)],
                cwd=source,
                stdout=log,
                stderr=subprocess.STDOUT,
                timeout=180,
            )
        records.append(
            {
                "kind": "execution",
                "variant": variant,
                "repeat": repeat,
                "binary_sha256": hashlib.sha256(binary.read_bytes()).hexdigest(),
                "returncode": result.returncode,
                "seconds": time.monotonic() - started,
            }
        )
        (root / "records.json").write_text(json.dumps(records, indent=2) + "\n")

for name, digest in effective_hashes.items():
    assert hashlib.sha256((root / "source" / name).read_bytes()).hexdigest() == digest
assert len(records) == 9 and all(row["returncode"] == 0 for row in records), records
(root / "complete.json").write_text(
    json.dumps(
        {
            "model_source_unchanged": True,
            "allocator_source_mode": args.source_mode,
            "cub": args.cub,
            "builds": 3,
            "executions": 6,
            "scope": "Debug qualification only. No full-state or paper-result equivalence established.",
        },
        indent=2,
    )
    + "\n"
)
