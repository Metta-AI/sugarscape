"""Audit full native qualification archives, retaining compiler failures."""

import argparse
import hashlib
import io
import json
from pathlib import Path
import re
import tarfile
import zipfile

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("output", type=Path)
parser.add_argument("archives", nargs="+", type=Path)
args = parser.parse_args()
reports = []
variants = {"dynasoar_no_cell", "baseline_aos", "baseline_soa"}
for archive_path in args.archives:
    with tarfile.open(archive_path) as archive:
        prefix = "qualification/native/"
        artifact = archive.extractfile(prefix + "artifact.zip").read()
        assert (
            hashlib.sha256(artifact).hexdigest()
            == "75421734305809c5999904082616996a904a19a5e43466cf076ec10660e559a1"
        )
        changes = []
        with zipfile.ZipFile(io.BytesIO(artifact)) as original:
            source_files = [m for m in original.infolist() if not m.is_dir()]
            for member in source_files:
                before = original.read(member)
                after = archive.extractfile(prefix + "source/" + member.filename).read()
                if before == after:
                    continue
                if member.filename == "dynasoar/allocator/allocator_handle.h":
                    assert before.count(b"allocator_->parallel_do<") == 4
                    assert after == before.replace(
                        b"allocator_->parallel_do<",
                        b"allocator_->template parallel_do<",
                    )
                else:
                    assert member.filename == "dynasoar/bitmap/bitmap.h"
                    expected = before
                    for method in ["atomic_add_scan_init", "atomic_add_scan"]:
                        old = f"&ThisClass::{method}>".encode()
                        assert expected.count(old) == 1
                        expected = expected.replace(
                            old, f"&ThisClass::template {method}<S>>".encode()
                        )
                    assert after == expected
                changes.append(
                    {
                        "file": member.filename,
                        "before_sha256": hashlib.sha256(before).hexdigest(),
                        "after_sha256": hashlib.sha256(after).hexdigest(),
                    }
                )
            config = original.read("dynasoar/example/sugarscape/configuration.h")
            assert b"kNumIterations = 10000;" in config and b"kSeed = 42;" in config
        records = json.load(archive.extractfile(prefix + "records.json"))
        builds = [r for r in records if r["kind"] == "build"]
        assert len(builds) == 3 and {r["variant"] for r in builds} == variants
        successful = {r["variant"] for r in builds if r["returncode"] == 0}
        for build in builds:
            assert "-DPARAM_SIZE=32" in build["command"]
            assert "-DPARAM_MAX_OBJ=262144" in build["command"]
            assert "-g" in build["command"] and "-DNDEBUG" not in build["command"]
            assert (
                f"example/sugarscape/{build['variant']}/sugarscape.cu"
                in build["command"]
            )
        executions = [r for r in records if r["kind"] == "execution"]
        assert len(executions) == 2 * len(successful)
        assert {(r["variant"], r["repeat"]) for r in executions} == {
            (v, n) for v in successful for n in range(2)
        }
        outputs = []
        for run in executions:
            assert run["returncode"] == 0
            binary = archive.extractfile(prefix + run["variant"]).read()
            assert hashlib.sha256(binary).hexdigest() == run["binary_sha256"]
            text = (
                archive.extractfile(
                    prefix + f"{run['variant']}-run-{run['repeat']}.log"
                )
                .read()
                .decode()
            )
            checksums = re.findall(r"^Checksum: (-?\d+)$", text, flags=re.MULTILINE)
            assert len(checksums) == 1
            timing = re.findall(r"^(\d+)(?:, (\d+))?$", text, flags=re.MULTILINE)
            assert len(timing) == 1 and int(timing[0][0]) > 0
            outputs.append(
                {
                    "variant": run["variant"],
                    "repeat": run["repeat"],
                    "checksum": int(checksums[0]),
                    "native_time_microseconds": int(timing[0][0]),
                }
            )
        terminal = json.load(archive.extractfile("qualification/terminal.json"))
        assert terminal["exit_code"] == (0 if len(successful) == 3 else 1)
        reports.append(
            {
                "archive": str(archive_path),
                "sha256": hashlib.sha256(archive_path.read_bytes()).hexdigest(),
                "source_files_checked": len(source_files),
                "declared_syntax_changes": changes,
                "builds": builds,
                "executions": outputs,
                "terminal": terminal,
            }
        )
args.output.parent.mkdir(parents=True, exist_ok=True)
with args.output.open("x") as output:
    json.dump(
        {
            "attempts": reports,
            "scope": "Operational qualification only. Native checksums sum agent type codes, not complete states. Repeats share one input and do not add scientific seeds.",
        },
        output,
        indent=2,
    )
    output.write("\n")
print(
    json.dumps(
        {
            "archives": len(reports),
            "executions": sum(len(r["executions"]) for r in reports),
        }
    )
)
