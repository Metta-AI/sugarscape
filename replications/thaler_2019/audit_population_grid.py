"""Independently verify complete population-grid records against original conditions."""

import argparse
import csv
import hashlib
import json
from pathlib import Path
import random

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("run", type=Path)
parser.add_argument("output", type=Path)
args = parser.parse_args()
assets = Path(__file__).parent
root = args.run
protocol = json.loads((root / "protocol.json").read_text())
manifest = root / "observer-manifest.json"
reference_manifest = (
    assets
    / "results/population-observer-qualification-2026-10-17/observer-manifest.json"
)
assert manifest.read_bytes() == reference_manifest.read_bytes()
assert (
    hashlib.sha256(manifest.read_bytes()).hexdigest()
    == protocol["observer_manifest_sha256"]
)
conditions = protocol["conditions"]
assert protocol["phase"] in ["full-native", "qualification"]
if protocol["phase"] == "full-native":
    expected = {("seq", 1, 500, False)}
    expected |= {
        (v, c, 500, False) for v in ["io", "tvar", "tarray"] for c in range(1, 9)
    }
    expected |= {
        (v, 1 if v == "seq" else 4, n, True)
        for v in ["seq", "io", "tvar", "tarray"]
        for n in [500, 1000, 1500, 2000, 2500]
    }
    assert len(conditions) == 45 and protocol["repetitions"] == 5
    assert {
        (c["variant"], c["caps"], c["agents"], c["rebirth"]) for c in conditions
    } == expected
    hardware = json.loads((root / "hardware.json").read_text())
    assert len(hardware["affinity"]) == 8
else:
    assert conditions == [
        {"variant": "seq", "caps": 1, "agents": 500, "rebirth": False},
        {"variant": "tarray", "caps": 1, "agents": 2500, "rebirth": True},
    ]
    assert protocol["repetitions"] == 1
schedule = [
    dict(c, repetition=r) for c in conditions for r in range(protocol["repetitions"])
]
random.Random(protocol["schedule_seed"]).shuffle(schedule)
assert json.loads((root / "schedule.json").read_text()) == schedule
records = [
    json.loads(line) for line in (root / "completed.jsonl").read_text().splitlines()
]
assert len(records) == len(schedule)
reference_path = assets / "results/population-replay-2026-10-17/population-1.csv"
with reference_path.open() as stream:
    reference = [(float(r["T"]), int(r["PopSize"])) for r in csv.DictReader(stream)]
for index, (record, condition) in enumerate(zip(records, schedule, strict=True)):
    assert record["index"] == index and record["condition"] == condition
    folder = root / f"run-{index:03d}"
    assert set(record["files_sha256"]) == {
        "command.json",
        "exit.json",
        "population.csv",
        "stderr.log",
    }
    for name, digest in record["files_sha256"].items():
        assert hashlib.sha256((folder / name).read_bytes()).hexdigest() == digest
    variant = condition["variant"]
    binary = json.loads((root / f"{variant}-binary.json").read_text())
    assert binary["compiler"] == "8.4.3"
    command = [binary["path"], str(condition["agents"]), str(condition["rebirth"])]
    if variant != "seq":
        command += ["+RTS", f"-N{condition['caps']}", "-RTS"]
    assert json.loads((folder / "command.json").read_text()) == command
    assert json.loads((folder / "exit.json").read_text())["exit_code"] == 0
    assert (folder / "stderr.log").read_bytes() == b""
    with (folder / "population.csv").open() as stream:
        reader = csv.DictReader(stream)
        assert reader.fieldnames == ["T", "PopSize"]
        rows = [(float(r["T"]), int(r["PopSize"])) for r in reader]
    assert [r[0] for r in rows] == list(range(1000))
    assert all(0 <= r[1] <= condition["agents"] for r in rows)
    assert record["observations"] == 1000
    assert (record["first"], record["last"]) == (rows[0][1], rows[-1][1])
    if not condition["rebirth"]:
        assert all(a[1] >= b[1] for a, b in zip(rows[:-1], rows[1:], strict=True))
        if variant == "seq":
            assert rows == reference
assert json.loads((root / "complete.json").read_text()) == {
    "completed_runs": len(records),
    "observations": len(records) * 1000,
}
report = {
    "phase": protocol["phase"],
    "validated_runs": len(records),
    "observations": len(records) * 1000,
    "records": records,
    "reference_sha256": hashlib.sha256(reference_path.read_bytes()).hexdigest(),
    "scope": "All declared process records, original condition identities, command/exit and trajectory hashes verified. Binary and hardware metadata are recorded provenance, not independent binary reconstruction. Qualification is not full-native coverage; no statistical equivalence claim.",
}
args.output.mkdir(exist_ok=False)
(args.output / "audit.json").write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps({k: v for k, v in report.items() if k != "records"}))
