"""Qualify passive timing instrumentation against complete native policy runs."""

import hashlib
import json
from pathlib import Path
import subprocess
import time

root = Path(__file__).resolve().parent
assert not (root / "qualification.json").exists()
protocol = json.loads((root / "protocol.json").read_bytes())
source = root / "RunPolicyTiming.java"
assert hashlib.sha256(source.read_bytes()).hexdigest() == protocol["timing_source_sha256"]
frontiers = root.parent / "oremland-frontier-transfer-001"
manifest = json.loads(
    (frontiers / "width-50-seed-20261021/manifest.json").read_bytes()
)
native = root / "native"
native.mkdir()
command = list(manifest["compile_command"])
command[-2:] = [str(native), str(source)]
with (root / "compile.log").open("x") as stream:
    subprocess.run(
        command, stdout=stream, stderr=subprocess.STDOUT, timeout=120, check=True
    )
timing_keys = {
    "elapsed_seconds",
    "setup_seconds",
    "simulation_seconds",
    "process_cpu_seconds",
}
receipts = []
for width in protocol["published_widths"]:
    manifest_path = frontiers / f"width-{width}-seed-20261021/manifest.json"
    manifest = json.loads(manifest_path.read_bytes())
    model = Path(manifest["command"][-3])
    assert hashlib.sha256(model.read_bytes()).hexdigest() == manifest["model_sha256"]
    work = root / f"width-{width}"
    work.mkdir()
    requests = [
        {
            "id": f"rate-{rate}-seed-{seed}",
            "seed": seed,
            "phase": 0,
            "clipped": False,
            "policy": [rate] * 200,
        }
        for rate in [0.0, 0.25, 0.5, 0.75]
        for seed in [0, 1]
    ]
    (work / "requests.jsonl").write_text(
        "".join(json.dumps(row) + "\n" for row in requests)
    )
    results = {}
    for recorder in ["original", "timed"]:
        output = work / f"{recorder}.jsonl"
        command = list(manifest["command"])
        command[3] = "120"
        command[-2:] = [str(work / "requests.jsonl"), str(output)]
        if recorder == "timed":
            command[10] = str(native) + ":" + command[10]
            command[11] = "RunPolicyTiming"
        started = time.monotonic()
        with (work / f"{recorder}.log").open("x") as stream:
            process = subprocess.run(
                command,
                stdout=stream,
                stderr=subprocess.STDOUT,
                timeout=160,
            )
        receipt = {
            "width": width,
            "recorder": recorder,
            "exit_code": process.returncode,
            "elapsed_seconds": time.monotonic() - started,
            "command": command,
            "manifest_sha256": hashlib.sha256(manifest_path.read_bytes()).hexdigest(),
        }
        receipts.append(receipt)
        (root / "commands.json").write_text(json.dumps(receipts, indent=2) + "\n")
        assert process.returncode == 0
        rows = [json.loads(line) for line in output.read_text().splitlines()]
        assert len(rows) == 8
        assert [row["id"] for row in rows] == [row["id"] for row in requests]
        assert all(row["steps"] == 50 for row in rows)
        results[recorder] = rows
    assert [
        {key: value for key, value in row.items() if key not in timing_keys}
        for row in results["original"]
    ] == [
        {key: value for key, value in row.items() if key not in timing_keys}
        for row in results["timed"]
    ]
    assert all(
        row["setup_seconds"] > 0
        and row["simulation_seconds"] > 0
        and row["process_cpu_seconds"] > 0
        and row["elapsed_seconds"] >= row["setup_seconds"] + row["simulation_seconds"]
        for row in results["timed"]
    )
    print(f"WIDTH={width} EIGHT_COMPLETE_NATIVE_OUTPUTS_EXACT", flush=True)
(root / "qualification.json").write_text(
    json.dumps(
        {
            "widths": protocol["published_widths"],
            "paired_inputs": 48,
            "native_executions": 96,
            "steps_per_execution": 50,
            "all_outputs_and_survivor_state_hashes_exact": True,
            "timing_fields_excluded_from_parity": sorted(timing_keys),
            "instrumentation_source_sha256": protocol["timing_source_sha256"],
            "class_sha256": hashlib.sha256(
                (native / "RunPolicyTiming.class").read_bytes()
            ).hexdigest(),
            "scope": "Complete native semantic qualification of passive timers. Contended qualification timings are not Table2 benchmark evidence.",
        },
        indent=2,
    )
    + "\n"
)
