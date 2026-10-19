"""Build unchanged artifact source in an isolated CUDA9.1/GCC5 environment."""

import argparse
import hashlib
import json
from pathlib import Path
import shlex
import shutil
import subprocess
import time
import zipfile

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("rootfs", type=Path)
parser.add_argument("artifact", type=Path)
parser.add_argument("output", type=Path)
args = parser.parse_args()
root = args.output.resolve()
root.mkdir(parents=True, exist_ok=False)
raw = args.artifact.read_bytes()
assert (
    hashlib.sha256(raw).hexdigest()
    == "75421734305809c5999904082616996a904a19a5e43466cf076ec10660e559a1"
)
(root / "artifact.zip").write_bytes(raw)
with zipfile.ZipFile(args.artifact) as archive:
    for member in archive.infolist():
        assert not Path(member.filename).is_absolute()
        assert ".." not in Path(member.filename).parts
    hashes = {
        m.filename: hashlib.sha256(archive.read(m)).hexdigest()
        for m in archive.infolist()
        if not m.is_dir()
    }
    archive.extractall(root / "source")
(root / "source-sha256.json").write_text(json.dumps(hashes, indent=2) + "\n")
inside = Path("/work/dynasoar-cuda91-native-001")
work = args.rootfs / inside.relative_to("/")
work.mkdir(parents=True, exist_ok=False)
shutil.copytree(root / "source", work / "source")
for name, command in [
    (
        "compiler",
        ["chroot", str(args.rootfs), "/usr/local/cuda-9.1/bin/nvcc", "--version"],
    ),
    ("host-compiler", ["chroot", str(args.rootfs), "g++", "--version"]),
    ("gpu", ["nvidia-smi", "-q"]),
]:
    (root / (name + ".txt")).write_text(subprocess.check_output(command, text=True))
records = []
for mode, size, limit in [
    ("debug", 32, 60),
    ("debug", 128, 60),
    ("debug", 1700, 180),
    ("release", 1700, 180),
]:
    label = f"{mode}-{size}"
    command = [
        "/usr/local/cuda-9.1/bin/nvcc",
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
        "-Ilib/cub",
        "-Xcudafe",
        "--diag_suppress=1427",
        "example/sugarscape/dynasoar_no_cell/sugarscape.cu",
        "-o",
        str(inside / label),
    ]
    if size != 1700:
        command.append(f"-DPARAM_SIZE={size}")
    started = time.monotonic()
    with (root / (label + "-build.log")).open("x") as log:
        build = subprocess.run(
            [
                "chroot",
                str(args.rootfs),
                "/bin/sh",
                "-c",
                "cd "
                + shlex.quote(str(inside / "source/dynasoar"))
                + " && "
                + shlex.join(command),
            ],
            stdout=log,
            stderr=subprocess.STDOUT,
            timeout=300,
        )
    records.append(
        {
            "kind": "build",
            "mode": mode,
            "grid_side": size,
            "command": command,
            "returncode": build.returncode,
            "elapsed_seconds": time.monotonic() - started,
        }
    )
    (root / "records.json").write_text(json.dumps(records, indent=2) + "\n")
    assert build.returncode == 0
    shutil.copy2(work / label, root / label)
    binary_hash = hashlib.sha256((root / label).read_bytes()).hexdigest()
    started = time.monotonic()
    with (root / (label + "-run.log")).open("x") as log:
        result = subprocess.run(
            ["timeout", str(limit), str(root / label)],
            stdout=log,
            stderr=subprocess.STDOUT,
            timeout=limit + 10,
        )
    records.append(
        {
            "kind": "execution",
            "mode": mode,
            "grid_side": size,
            "returncode": result.returncode,
            "limit_seconds": limit,
            "elapsed_seconds": time.monotonic() - started,
            "binary_sha256": binary_hash,
        }
    )
    (root / "records.json").write_text(json.dumps(records, indent=2) + "\n")
    for name, digest in hashes.items():
        assert (
            hashlib.sha256((work / "source" / name).read_bytes()).hexdigest() == digest
        )
    assert result.returncode == 0
(root / "complete.json").write_text(
    json.dumps(
        {
            "executions": 4,
            "source_files_verified": len(hashes),
            "source_edits": 0,
            "scope": "Execution qualification, not full-state equivalence or historical hardware performance.",
        },
        indent=2,
    )
    + "\n"
)
