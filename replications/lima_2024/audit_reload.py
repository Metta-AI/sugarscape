"""Evaluate the preregistered reload control against native files and logs."""

import argparse
import hashlib
import json
from pathlib import Path
import re

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("run", type=Path)
parser.add_argument("output", type=Path)
parser.add_argument("--native-log", default="jacamo-live-001.log")
parser.add_argument("--reexport", default="agent-399-reexport-001.asl")
args = parser.parse_args()
original = args.run / "agent-399-input.asl"
reexport = args.run / args.reexport
native = args.run / args.native_log
protocol = json.loads((args.run / "protocol.json").read_text())
assert hashlib.sha256(original.read_bytes()).hexdigest() == protocol["saved_asl_sha256"]
before = original.read_text()
after = reexport.read_text()
log = re.sub(r"\x1b\[[0-9;]*[A-Za-z]", "", native.read_text())
assert "asl_file_name: list/399.asl" in log
assert "Agent 399 removed from the simulation" in log
assert "Tupla - path: 1-3-3" in log
assert protocol["retained_belief"] in before.splitlines()
assert protocol["retained_belief"] in after.splitlines()
old_plans = [line for line in before.splitlines() if line.startswith("@")]
new_plans = [line for line in after.splitlines() if line.startswith("@")]
normalized = [
    line.replace(',url("file:src/agt/list/399.asl")', "") for line in new_plans
]
assert old_plans == normalized
assert len(old_plans) == 39
old_score = re.findall(r"^score\((\d+)\)\.$", before, re.MULTILINE)
new_score = re.findall(r"^score\((\d+)\)\.$", after, re.MULTILINE)
assert old_score == [str(protocol["saved_score"])]
assert len(new_score) == 1
report = {
    "native_saved_file_selected": True,
    "retained_belief_preserved": True,
    "plans_preserved": len(old_plans),
    "normalization": "Remove only the additional saved-file URL source annotation.",
    "score_before": int(old_score[0]),
    "expected_score_after": 2,
    "observed_score_after": int(new_score[0]),
    "score_increment_passed": int(new_score[0]) == 2,
    "saved_departure_trigger_present": "initial_print1." in before.splitlines(),
    "native_mining_completion_messages": log.count("[399] Finish handling"),
    "reexport_and_departure_observed": True,
    "files_sha256": {
        path.name: hashlib.sha256(path.read_bytes()).hexdigest()
        for path in (original, reexport, native, args.run / "protocol.json")
    },
    "scope": (
        "Additional checkpoint-reentry control. Evaluate the declared score criterion "
        "without changing it. Full trajectories and identity conservation "
        "are audited separately; this is not a whole-paper negative verdict."
    ),
    "completed_study": False,
}
with args.output.open("x") as stream:
    stream.write(json.dumps(report, indent=2) + "\n")
print(json.dumps(report))
