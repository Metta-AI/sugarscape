"""Audit the complete full-size batch against retained qualification provenance."""

import argparse
import hashlib
import json
from pathlib import Path
import re
import statistics
import tarfile

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("archive", type=Path)
parser.add_argument("qualification_archive", type=Path)
parser.add_argument("output", type=Path)
args = parser.parse_args()
assert (
    hashlib.sha256(args.qualification_archive.read_bytes()).hexdigest()
    == "c4f1effae4f330d8a07e60a9d6c81d372425773b3f8d5d26243b4e2af8c6eaa2"
)
with tarfile.open(args.qualification_archive) as qualified:
    hashes = json.load(
        qualified.extractfile("qualification/native/effective-source-sha256.json")
    )
    for name, digest in hashes.items():
        assert (
            hashlib.sha256(
                qualified.extractfile("qualification/native/source/" + name).read()
            ).hexdigest()
            == digest
        )
    config = (
        qualified.extractfile(
            "qualification/native/source/dynasoar/example/sugarscape/configuration.h"
        )
        .read()
        .decode()
    )
    for expected in [
        "kSize = 1700;",
        "kNumObjects = 64*64*64*64;",
        "kNumIterations = 10000;",
        "kSeed = 42;",
    ]:
        assert expected in config
with tarfile.open(args.archive) as archive:
    assert json.load(archive.extractfile("run/terminal.json"))["exit_code"] == 0
    assert (
        json.load(archive.extractfile("run/native/effective-source-sha256.json"))
        == hashes
    )
    records = json.load(archive.extractfile("run/native/records.json"))
    builds = [r for r in records if r["kind"] == "build"]
    runs = [r for r in records if r["kind"] == "execution"]
    expected = {
        ("dynasoar_no_cell", "debug"): 1,
        ("dynasoar_no_cell", "release"): 5,
        ("baseline_aos", "release"): 5,
        ("baseline_soa", "release"): 5,
    }
    assert len(builds) == 4 and len(runs) == 16
    assert {(b["variant"], b["mode"]) for b in builds} == set(expected)
    assert {(r["variant"], r["mode"], r["repeat"]) for r in runs} == {
        (v, m, i) for (v, m), n in expected.items() for i in range(n)
    }
    for b in builds:
        command = b["command"]
        assert b["returncode"] == 0 and "-O3" in command
        assert not any(arg.startswith("-DPARAM_") for arg in command)
        assert ("-DNDEBUG" in command) == (b["mode"] == "release")
        assert ("-g" in command) == (b["mode"] == "debug")
        assert f"example/sugarscape/{b['variant']}/sugarscape.cu" in command
    audited = []
    for r in runs:
        assert r["returncode"] == 0
        label = f"{r['variant']}-{r['mode']}"
        binary = archive.extractfile("run/native/" + label).read()
        assert hashlib.sha256(binary).hexdigest() == r["binary_sha256"]
        log = (
            archive.extractfile(f"run/native/{label}-run-{r['repeat']}.log")
            .read()
            .decode()
        )
        timing = re.findall(r"^(\d+)(?:, (\d+))?$", log, flags=re.MULTILINE)
        assert len(timing) == 1
        total = int(timing[0][0])
        enumeration = int(timing[0][1]) if timing[0][1] else 0
        assert 0 <= enumeration <= total and total > 0
        checksums = re.findall(r"^Checksum: (-?\d+)$", log, flags=re.MULTILINE)
        assert len(checksums) == (1 if r["mode"] == "debug" else 0)
        audited.append(
            dict(
                variant=r["variant"],
                mode=r["mode"],
                repeat=r["repeat"],
                total_microseconds=total,
                enumeration_microseconds=enumeration,
            )
        )
summary = {
    v: {
        "minimum_total_seconds": min(
            r["total_microseconds"]
            for r in audited
            if r["variant"] == v and r["mode"] == "release"
        )
        / 1e6,
        "median_total_seconds": statistics.median(
            r["total_microseconds"]
            for r in audited
            if r["variant"] == v and r["mode"] == "release"
        )
        / 1e6,
        "median_enumeration_seconds": statistics.median(
            r["enumeration_microseconds"]
            for r in audited
            if r["variant"] == v and r["mode"] == "release"
        )
        / 1e6,
    }
    for v in ["dynasoar_no_cell", "baseline_aos", "baseline_soa"]
}
with args.output.open("x") as handle:
    json.dump(
        dict(
            archive_sha256=hashlib.sha256(args.archive.read_bytes()).hexdigest(),
            runs=audited,
            summary=summary,
            scope="Execution and provenance audit; does not validate complete model state or historical timing equivalence.",
        ),
        handle,
        indent=2,
    )
    handle.write("\n")
print(json.dumps(summary))
