"""Audit every saved state from one native GPU condition and reconstruct initialization."""

import argparse
import hashlib
import json
import math
import subprocess
import tarfile
import xml.etree.ElementTree as ET
from pathlib import Path

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("archive", type=Path)
parser.add_argument("requested", type=int)
parser.add_argument("output", type=Path)
args = parser.parse_args()
args.output.mkdir()
width = math.isqrt(args.requested)
count = width * width
prefix = f"cells-{args.requested}/iterations/"


def cells(stream):
    events = ET.iterparse(stream, events=("start", "end"))
    _, root = next(events)
    for event, element in events:
        if event == "end" and element.tag == "itno":
            yield int(element.text)
        if event == "end" and element.tag == "xagent":
            assert element.findtext("name") == "Agent"
            row = {
                "pos": [float(element.findtext(k)) for k in ["x", "y"]],
                "target_pos": [
                    float(element.findtext(k)) for k in ["target_pos_x", "target_pos_y"]
                ],
            }
            row.update(
                {
                    k: int(element.findtext(k))
                    for k in [
                        "agent_id",
                        "state",
                        "sugar_level",
                        "metabolism",
                        "env_sugar_level",
                        "max_env_sugar_level",
                    ]
                }
            )
            yield row
            root.clear()


with tarfile.open(args.archive) as archive:
    initial_stream = cells(archive.extractfile(prefix + "0.xml"))
    assert next(initial_stream) == 0
    initial = list(initial_stream)
    assert len(initial) == count
    initial_path = args.output / "initial.json"
    initial_path.write_text(json.dumps({"Agent": initial}) + "\n")
    capacities = [row["max_env_sugar_level"] for row in initial]
    del initial
    snapshots = []
    for member in archive:
        if not member.name.startswith(prefix) or not member.name.endswith(".xml"):
            continue
        step = int(Path(member.name).stem)
        stream = cells(archive.extractfile(member))
        assert next(stream) == step
        population = 0
        seen = 0
        for index, row in enumerate(stream):
            assert index < count
            assert row["pos"] == [index // width + 0.5, index % width + 0.5]
            assert row["max_env_sugar_level"] == capacities[index]
            assert 0 <= row["env_sugar_level"] <= capacities[index]
            assert row["state"] in range(4)
            assert all(math.isfinite(v) for v in row["target_pos"])
            population += row["state"] != 0
            seen += 1
        assert seen == count
        snapshots.append({"step": step, "cells": seen, "population": population})
assert sorted(row["step"] for row in snapshots) == list(range(101))
command = [
    "python3",
    str(Path(__file__).with_name("initialize.py")),
    str(initial_path),
    str(args.output / "initialization-audit.json"),
    "--requested-cells",
    str(args.requested),
]
result = subprocess.run(command, capture_output=True, text=True)
(args.output / "initialization-command.json").write_text(
    json.dumps(
        {
            "command": command,
            "exit_code": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
        },
        indent=2,
    )
    + "\n"
)
assert result.returncode == 0, result.stderr
(args.output / "audit.json").write_text(
    json.dumps(
        {
            "requested_cells": args.requested,
            "actual_cells": count,
            "snapshots": sorted(snapshots, key=lambda row: row["step"]),
            "agent_observations": count * 101,
            "initialization_fields": count * 8,
            "checks": [
                "complete iteration sequence",
                "fixed unique positions",
                "fixed capacity",
                "resource bounds",
                "state range",
                "finite targets",
                "independent initialization",
            ],
            "archive_sha256": hashlib.file_digest(
                args.archive.open("rb"), "sha256"
            ).hexdigest(),
            "scope": "Native GPU structural checks and initial-state reconstruction; not transition or historical timing equivalence.",
            "completed_study": False,
        },
        indent=2,
    )
    + "\n"
)
print(f"Audited {count * 101} native agent observations and {count * 8} initial fields")
