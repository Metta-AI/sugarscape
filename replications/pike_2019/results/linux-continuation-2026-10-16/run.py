import concurrent.futures
import hashlib
import json
import subprocess
import sys
from pathlib import Path

root = Path(__file__).resolve().parent
source = Path("/root/sugarscape/pike-portability-001")
for name, digest in json.loads((root / "plan.json").read_text())["dependencies"].items():
    assert hashlib.sha256((source / name).read_bytes()).hexdigest() == digest
plan = json.loads((root / "plan.json").read_text())


def run(condition):
    phase, start, stop = (condition[k] for k in ("phase", "start", "stop"))
    output = root / f"phase{phase}-{start}-{stop}"
    command = [
        sys.executable,
        str(source / "run_segment.py"),
        str(source / f"frozen-phase{phase}"),
        str(source / "engine"),
        str(source / "library"),
        str(phase),
        str(start),
        str(stop),
        str(output),
    ]
    with (root / f"phase{phase}-{start}-{stop}.log").open("x") as log:
        subprocess.run(command, stdout=log, stderr=subprocess.STDOUT, check=True)
        auditor = {1: "audit_phase1.py", 2: "audit_phase2.py", 3: "audit_phase3_movement.py"}[phase]
        subprocess.run(
            [
                sys.executable,
                str(source / auditor),
                str(output),
                "prefix",
                str(root / f"audit-phase{phase}-{start}-{stop}"),
                "--start-index",
                str(start),
            ],
            stdout=log,
            stderr=subprocess.STDOUT,
            check=True,
        )
    return condition


with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
    completed = list(pool.map(run, plan["conditions"]))
(root / "production-complete.json").write_text(json.dumps({"completed": completed}) + "\n")
