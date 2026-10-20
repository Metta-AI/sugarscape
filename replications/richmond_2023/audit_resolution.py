"""Verify a full native passive counter trace and unchanged population output."""

import argparse
import csv
import hashlib
import json
from pathlib import Path
import re

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("evidence", type=Path)
parser.add_argument("unmodified_snapshot", type=Path)
parser.add_argument("output", type=Path)
args = parser.parse_args()
root = args.evidence
protocol_path = (
    Path(__file__).parent
    / "results/resolution-observer-launch-2026-10-17/protocol.json"
)
protocol = json.loads(protocol_path.read_text())
assert int((root / "exit-code.txt").read_text()) == 0
assert (
    hashlib.sha256((root / "main.cu").read_bytes()).hexdigest()
    == protocol["observer_sha256"]
)
reference_path = args.unmodified_snapshot / "native.csv"
assert (
    hashlib.sha256(reference_path.read_bytes()).hexdigest()
    == "67795fa7785278d5d22f3dd4300dc074f83ca07406039950f8b01fe42e424775"
)
with reference_path.open() as stream:
    reference = list(csv.DictReader(stream))[:100]
with (root / "run/performance_scalingperStep.csv").open() as stream:
    native = list(csv.DictReader(stream))
assert len(native) == len(reference) == 100
fields = ["repetition", "grid_width", "pop_size", "p_occupation", "step", "pop_count"]
assert [[r[f] for f in fields] for r in native] == [
    [r[f] for f in fields] for r in reference
]
log = (root / "run/stderr.log").read_text()
trace = re.findall(
    r"^RESOLUTION_TRACE,performance_scaling,0,256,(\d+),(\d+),(\d+)$", log, re.MULTILINE
)
assert len(trace) == log.count("RESOLUTION_TRACE,") == 100
rows = [
    {
        "step": int(step),
        "before": int(before),
        "after": int(after),
        "iterations": int(after) - int(before),
    }
    for step, before, after in trace
]
assert [r["step"] for r in rows] == list(range(100))
assert rows[0]["before"] == 0
assert all(rows[i]["before"] == rows[i - 1]["after"] for i in range(1, 100))
assert all(1 <= r["iterations"] <= 9 for r in rows)
cutoff = [r for r in rows if r["before"] >= 9]
assert cutoff and all(r["iterations"] == 1 for r in cutoff)
report = {
    "population_observations": 100,
    "population_exact_matches": 100,
    "first_step_starting_at_or_above_cutoff": cutoff[0]["step"],
    "steps_starting_at_or_above_cutoff": len(cutoff),
    "final_counter": rows[-1]["after"],
    "counter_resets_between_steps": 0,
    "trace": rows,
    "input_sha256": {
        str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
        for p in [
            root / "main.cu",
            root / "run/stderr.log",
            root / "run/performance_scalingperStep.csv",
            root / "exit-code.txt",
        ]
    },
    "scope": "Passive first-condition counter diagnostic with population parity. No correction, individual-state equivalence, timing comparison, or whole-paper verdict.",
}
args.output.mkdir(parents=True, exist_ok=False)
(args.output / "audit.json").write_text(json.dumps(report, indent=2) + "\n")
print(
    json.dumps({k: v for k, v in report.items() if k not in ["trace", "input_sha256"]})
)
