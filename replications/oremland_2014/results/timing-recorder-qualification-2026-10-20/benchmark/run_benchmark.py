"""Run the frozen timing batches after this task's heavy local jobs terminate."""

import hashlib
import json
import os
from pathlib import Path
import platform
import subprocess
import time

root = Path(__file__).resolve().parent
plan = json.loads((root / "protocol.json").read_bytes())
for name, digest in plan["controller_sha256"].items():
    assert hashlib.sha256((root / name).read_bytes()).hexdigest() == digest
qualified = root.parent / "oremland-timing-qualification-001"
assert hashlib.sha256((qualified / "qualification.json").read_bytes()).hexdigest() == plan[
    "qualification_sha256"
]
assert hashlib.sha256(
    (qualified / "native/RunPolicyTiming.class").read_bytes()
).hexdigest() == plan["timing_class_sha256"]
assert not (root / "admission.json").exists()
deadline = time.monotonic() + plan["observation_limit_seconds"]
while True:
    live = []
    for pid in plan["wait_for_owned_pids"]:
        status = subprocess.run(
            ["ps", "-p", str(pid), "-o", "pid="],
            capture_output=True,
            text=True,
            timeout=10,
        )
        assert status.returncode in [0, 1]
        if status.returncode == 0:
            live.append(pid)
    if not live:
        break
    assert time.monotonic() < deadline
    time.sleep(60)
for name, digest in plan["controller_sha256"].items():
    assert hashlib.sha256((root / name).read_bytes()).hexdigest() == digest
(root / "admission.json").write_text(
    json.dumps(
        {
            "unix": time.time(),
            "platform": platform.platform(),
            "machine": platform.machine(),
            "cpu_count": os.cpu_count(),
            "load_average": os.getloadavg(),
            "owned_dependencies_terminal": plan["wait_for_owned_pids"],
            "no_machine_wide_idle_claim": True,
            "protocol_sha256": hashlib.sha256(
                (root / "protocol.json").read_bytes()
            ).hexdigest(),
        },
        indent=2,
    )
    + "\n"
)
for width in plan["width_order"]:
    manifest = json.loads((root / f"manifest-{width}.json").read_bytes())
    command = list(manifest["command"])
    classpath = {Path(p).name: Path(p) for p in command[10].split(":")}
    for name, digest in manifest["jars"].items():
        assert hashlib.sha256(classpath[name].read_bytes()).hexdigest() == digest
    assert hashlib.sha256(Path(command[-3]).read_bytes()).hexdigest() == manifest[
        "model_sha256"
    ]
    work = root / f"width-{width}"
    work.mkdir()
    rows = [
        {
            "id": f"warmup-{i}",
            "seed": 1000 + i,
            "policy": plan["policy"],
            "phase": plan["phase"],
            "clipped": plan["clipped"],
        }
        for i in range(plan["warmup_runs_per_width"])
    ]
    rows += [
        {
            "id": f"repeat-{repeat}-input-{i}",
            "seed": 20000 + 10000 * repeat + i,
            "policy": plan["policy"],
            "phase": plan["phase"],
            "clipped": plan["clipped"],
        }
        for repeat in range(plan["repetitions"])
        for i in range(plan["simulation_counts"][str(width)])
    ]
    (work / "requests.jsonl").write_text(
        "".join(json.dumps(row) + "\n" for row in rows)
    )
    command[3] = str(plan["per_width_timeout_seconds"])
    command[10] = str(qualified / "native") + ":" + command[10]
    command[11] = "RunPolicyTiming"
    command[-2:] = [str(work / "requests.jsonl"), str(work / "results.jsonl")]
    before = os.getloadavg()
    started = time.time()
    with (work / "native.log").open("x") as stream:
        process = subprocess.run(
            command,
            stdout=stream,
            stderr=subprocess.STDOUT,
            timeout=plan["per_width_timeout_seconds"] + 60,
        )
    (work / "terminal.json").write_text(
        json.dumps(
            {
                "exit_code": process.returncode,
                "elapsed_seconds": time.time() - started,
                "load_before": before,
                "load_after": os.getloadavg(),
                "command": command,
                "native_inputs": len(rows),
            },
            indent=2,
        )
        + "\n"
    )
    assert process.returncode == 0
    print(f"WIDTH={width} NATIVE_INPUTS={len(rows)} COMPLETE", flush=True)
with (root / "audit.log").open("x") as stream:
    subprocess.run(
        [
            "/Users/relh/Code/workspace/sugarscape-replications/.venv/bin/python",
            str(root / "audit_benchmark.py"),
            str(root),
            str(root / "audit.json"),
        ],
        stdout=stream,
        stderr=subprocess.STDOUT,
        timeout=300,
        check=True,
    )
print("ALL_TABLE2_TIMING_BATCHES_AUDITED", flush=True)
