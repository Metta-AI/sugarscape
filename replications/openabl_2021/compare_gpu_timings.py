"""Compare retained whole-process GPU timings without inferring hardware equivalence."""

import argparse
import csv
import hashlib
import json
from pathlib import Path
import re
import tarfile

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("output", type=Path)
args = parser.parse_args()
root = Path(__file__).resolve().parent
args.output.mkdir(parents=True, exist_ok=False)
paper_path = root / "paper-targets/figure4.json"
paper = json.loads(paper_path.read_text())
targets = {
    p["requested_cells"]: p for p in paper["points"] if p["backend"] == "flamegpu"
}
assert sorted(targets) == [250 * 2**i for i in range(13)]
qualification = root / "gpu-condition/native-evidence.tar.gz"
with tarfile.open(qualification) as archive:
    smallest = archive.extractfile("qualification.log").read()
rows = []
receipts = []
for size, target in sorted(targets.items()):
    if size == 250:
        raw = smallest
        origin = "gpu-condition/native-evidence.tar.gz:qualification.log"
    else:
        path = root / f"gpu-grid/native-source-readback/cells-{size}/run.log"
        raw = path.read_bytes()
        origin = str(path.relative_to(root))
    log = raw.decode()
    assert re.findall(r"Exit status: (\d+)", log) == ["0"]
    elapsed = re.findall(r"Elapsed \(wall clock\) time \(h:mm:ss or m:ss\): (\S+)", log)
    assert len(elapsed) == 1
    components = [float(x) for x in elapsed[0].split(":")]
    assert len(components) in [2, 3]
    wall = sum(v * 60**i for i, v in enumerate(reversed(components)))
    engine = re.findall(r"Total Processing time: ([\d.]+) \(ms\)", log)
    assert len(engine) == 1
    engine_seconds = float(engine[0]) / 1000
    assert 0 < engine_seconds < wall
    rows.append(
        {
            "requested_cells": size,
            "published_seconds": target["runtime_seconds"],
            "native_wall_seconds": wall,
            "engine_reported_seconds": engine_seconds,
            "native_over_published": wall / target["runtime_seconds"],
        }
    )
    receipts.append(
        {
            "requested_cells": size,
            "log": origin,
            "sha256": hashlib.sha256(raw).hexdigest(),
        }
    )
with (args.output / "timings.csv").open("w") as stream:
    writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
    writer.writeheader()
    writer.writerows(rows)
(args.output / "comparison.json").write_text(
    json.dumps(
        {
            "conditions": rows,
            "input_logs": receipts,
            "paper_targets_sha256": hashlib.sha256(paper_path.read_bytes()).hexdigest(),
            "qualification_archive_sha256": hashlib.sha256(
                qualification.read_bytes()
            ).hexdigest(),
            "historical_hardware": "Intel i5-4690K / Titan Xp; paper configuration",
            "native_hardware": "H100; retained CPU and storage runtime differ from the paper",
            "native_repetitions_per_condition": 1,
            "timing_scope": "Whole runner subprocess, including initialization and per-step XML. Engine-reported CUDA-event span also encloses the XML-writing loop; it is not kernel-only time.",
            "limitations": "Different hardware/toolchain; source revision not proven historical; no timing uncertainty estimated from one observation; ratios are descriptive, not a replication verdict.",
            "completed_study": False,
        },
        indent=2,
    )
    + "\n"
)
print(f"Compared {len(rows)} published and native GPU timing conditions")
