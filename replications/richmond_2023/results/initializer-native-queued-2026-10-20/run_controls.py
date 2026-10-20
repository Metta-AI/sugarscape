"""Execute separately labelled controls only after exact released-state qualification."""

import csv
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tarfile
import time

root = Path(__file__).resolve().parent
protocol = json.loads((root / "protocol.json").read_text())
started = time.monotonic()
deadline = started + protocol["wall_seconds"]
qualified = root.parent / "richmond-qualification-001"
engine = qualified / "engine"
source = root / "source"
build = root / "build"
commands = []
completed = []


def run(command, label, seconds, cwd=root, env=None):
    remaining = int(deadline - time.monotonic())
    assert remaining > 0, "Overall execution bound exhausted"
    bounded = [
        "/usr/bin/timeout",
        "--kill-after=10",
        str(min(seconds, remaining)),
        *command,
    ]
    record = {"command": bounded, "cwd": str(cwd), "label": label}
    commands.append(record)
    (root / "commands.json").write_text(json.dumps(commands, indent=2) + "\n")
    with (root / (label + ".log")).open("x") as stream:
        process = subprocess.run(
            bounded, cwd=cwd, env=env, stdout=stream, stderr=subprocess.STDOUT
        )
    record["exit_code"] = process.returncode
    (root / "commands.json").write_text(json.dumps(commands, indent=2) + "\n")
    assert process.returncode == 0, record


try:
    assert not source.exists() and not build.exists()
    for checkout, revision in [
        (qualified / "benchmark", protocol["source_revision"]),
        (engine, protocol["engine_revision"]),
    ]:
        assert (
            subprocess.check_output(
                ["git", "-C", str(checkout), "rev-parse", "HEAD"], text=True
            ).strip()
            == revision
        )
        subprocess.run(
            ["git", "-C", str(checkout), "diff", "--quiet", "HEAD", "--"], check=True
        )
    with (root / "original-source.tar").open("xb") as stream:
        subprocess.run(
            [
                "git",
                "-C",
                str(qualified / "benchmark"),
                "archive",
                protocol["source_revision"],
            ],
            stdout=stream,
            check=True,
        )
    source.mkdir()
    with tarfile.open(root / "original-source.tar") as bundle:
        assert all(member.isfile() or member.isdir() for member in bundle.getmembers())
        assert all(
            not Path(member.name).is_absolute() and ".." not in Path(member.name).parts
            for member in bundle.getmembers()
        )
        bundle.extractall(source)
    run(["nvidia-smi"], "gpu", 30)
    run(["nvcc", "--version"], "cuda", 30)
    run(["g++", "--version"], "compiler", 30)
    assert len(protocol["variants"]) == 9
    assert [item["variant"] for item in protocol["variants"][:2]] == [
        "released",
        "combined_m4_c4_direct",
    ]
    initial_by_metabolism = {}
    reference_peaks = []
    for item in protocol["variants"]:
        variant = item["variant"]
        candidate = root / "variants" / variant / "src/main.cu"
        assert (
            hashlib.sha256(candidate.read_bytes()).hexdigest() == item["source_sha256"]
        )
        shutil.copyfile(candidate, source / "src/main.cu")
        if variant == "released":
            run(
                [
                    "cmake",
                    str(source),
                    "-B",
                    str(build),
                    "-DCMAKE_BUILD_TYPE=Release",
                    "-DCMAKE_CUDA_ARCHITECTURES=90",
                    "-DFLAMEGPU_ROOT=" + str(engine),
                    "-DFLAMEGPU_SEATBELTS=OFF",
                    "-DFLAMEGPU_SHARE_USAGE_STATISTICS=OFF",
                ],
                "configure",
                300,
            )
        run(["cmake", "--build", str(build), "-j", "8"], variant + "-build", 1000)
        binary = build / "bin/Release/submodel-benchmark"
        directory = root / "runs" / variant
        directory.mkdir(parents=True)
        (directory / "binary-sha256.txt").write_text(
            hashlib.sha256(binary.read_bytes()).hexdigest() + "\n"
        )
        env = dict(os.environ, FLAMEGPU2_INC_DIR=str(engine / "include"))
        run([str(binary)], variant + "-native", 300, directory, env)
        state = directory / "state.csv"
        digest = hashlib.sha256(state.read_bytes()).hexdigest()
        with (directory / "initial-cells.csv").open() as stream:
            cells = list(csv.DictReader(stream))
        assert len(cells) == 65536
        active = [
            {key: row[key] for key in ["id", "x", "y", "status", "sugar", "metabolism"]}
            for row in cells
            if row["status"] == "1"
        ]
        metabolism = item["metabolism_maximum"]
        if metabolism in initial_by_metabolism:
            assert active == initial_by_metabolism[metabolism], (
                "Fixed-metabolism initial agent attributes changed"
            )
        else:
            initial_by_metabolism[metabolism] = active
        peaks = [
            line
            for line in (root / (variant + "-native.log")).read_text().splitlines()
            if line.startswith("HOTSPOT,")
        ]
        assert len(peaks) == 54
        if variant == "released":
            assert digest == protocol["released_state_sha256"], (
                "Released full-state parity failed"
            )
            reference_peaks = peaks
        else:
            assert peaks == reference_peaks, "Peak sequence changed"
        if variant == "combined_m4_c4_direct":
            assert digest == protocol["combined_state_sha256"], (
                "Combined baseline full-state parity failed"
            )
        completed.append(
            {
                "variant": variant,
                "state_sha256": digest,
                "initial_cells_sha256": hashlib.sha256(
                    (directory / "initial-cells.csv").read_bytes()
                ).hexdigest(),
                "initial_active_records": len(active),
                "fixed_metabolism_initial_attributes_exact": True,
                "peaks_match_released": peaks == reference_peaks,
            }
        )
        (root / "completed.json").write_text(json.dumps(completed, indent=2) + "\n")
    assert len(completed) == 9
finally:
    (root / "terminal.json").write_text(
        json.dumps(
            {
                "completed_variants": completed,
                "elapsed_seconds": time.monotonic() - started,
                "scope": "Native execution and baseline/initial parity only. Independent variant-state audit remains required.",
            },
            indent=2,
        )
        + "\n"
    )
    archive = root / "native-evidence.tar.gz"
    with tarfile.open(archive, "x:gz") as bundle:
        for path in sorted(root.iterdir()):
            if path.name not in {"build", "source", archive.name}:
                bundle.add(path, arcname=path.name)
    assert archive.stat().st_size <= 256 * 1024**2
    print(
        json.dumps(
            {
                "archive": str(archive),
                "bytes": archive.stat().st_size,
                "sha256": hashlib.sha256(archive.read_bytes()).hexdigest(),
            }
        ),
        flush=True,
    )
