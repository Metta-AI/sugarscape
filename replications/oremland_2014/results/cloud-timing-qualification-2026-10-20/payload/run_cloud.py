"""Qualify the native recorder on the CPU host, then run a separately gated benchmark."""
from pathlib import Path
import hashlib
import json
import os
import platform
import subprocess
import sys
import tarfile
import time

root = Path(__file__).resolve().parent
mode = sys.argv[1]
assert mode in ["qualification", "benchmark"]
pins = json.loads((root / "payload-sha256.json").read_bytes())
for name, digest in pins.items():
    assert hashlib.sha256((root / name).read_bytes()).hexdigest() == digest
plan = json.loads((root / "protocol.json").read_bytes())
if mode == "benchmark":
    gate = json.loads((root / "benchmark-gate.json").read_bytes())
    assert gate["local_recorder_parity_verified"] and gate["old_watcher_stopped_before_admission"]
    assert gate["qualification_sha256"] == hashlib.sha256((root / "qualification/complete.json").read_bytes()).hexdigest()
output = root / mode
output.mkdir()
(output / "protocol.json").write_bytes((root / "protocol.json").read_bytes())
affinity = sorted(os.sched_getaffinity(0))
java = subprocess.run(["java", "-version"], capture_output=True, text=True, check=True)
hardware = {"platform": platform.platform(), "machine": platform.machine(), "affinity_allowed": affinity,
            "pinned_cpu": affinity[0], "java_version": java.stderr, "load_average": os.getloadavg(),
            "cpu_model": next(line.split(":", 1)[1].strip() for line in Path("/proc/cpuinfo").read_text().splitlines() if line.startswith("model name")),
            "protocol_sha256": hashlib.sha256((root / "protocol.json").read_bytes()).hexdigest(), "unix": time.time(),
            "scope": "One allowed logical CPU pinned; task-owned container has eight-core CFS quota. Host contention is not excluded; no historical hardware identity claim."}
(output / "admission.json").write_text(json.dumps(hardware, indent=2) + "\n")
order = json.loads((root / "classpath.json").read_bytes())
classpath = ":".join([str(root / "native"), *[str(root / "jars" / name) for name in order]])
count = 0
for width in plan["width_order"]:
    work = output / f"width-{width}"
    work.mkdir()
    if mode == "qualification":
        requests = [json.loads(line) for line in (root / "reference" / str(width) / "requests.jsonl").read_text().splitlines()]
    else:
        requests = [{"id": f"warmup-{i}", "seed": 1000 + i, "policy": plan["policy"], "phase": 0, "clipped": False} for i in range(100)]
        requests += [{"id": f"repeat-{repeat}-input-{i}", "seed": 20000 + 10000 * repeat + i, "policy": plan["policy"], "phase": 0, "clipped": False}
                     for repeat in range(3) for i in range(plan["simulation_counts"][str(width)])]
    (work / "requests.jsonl").write_text("".join(json.dumps(row) + "\n" for row in requests))
    seconds = 120 if mode == "qualification" else plan["per_width_timeout_seconds"]
    command = ["timeout", "--signal=TERM", "--kill-after=30", str(seconds), "taskset", "-c", str(affinity[0]),
               "java", "-Xmx512m", "-XX:ActiveProcessorCount=1", "-Djava.awt.headless=true", "-Dfile.encoding=UTF-8",
               "-cp", classpath, "RunPolicyTiming", str(root / "models" / str(width) / "oremland.nlogo"),
               str(work / "requests.jsonl"), str(work / "results.jsonl")]
    started = time.monotonic()
    with (work / "native.log").open("x") as stream:
        process = subprocess.run(command, stdout=stream, stderr=subprocess.STDOUT, timeout=seconds + 60)
    (work / "terminal.json").write_text(json.dumps({"exit_code": process.returncode, "elapsed_seconds": time.monotonic() - started,
        "command": command, "native_inputs": len(requests), "load_after": os.getloadavg()}, indent=2) + "\n")
    assert process.returncode == 0
    results = [json.loads(line) for line in (work / "results.jsonl").read_text().splitlines()]
    assert len(results) == len(requests)
    if mode == "qualification":
        reference = [json.loads(line) for line in (root / "reference" / str(width) / "timed.jsonl").read_text().splitlines()]
        excluded = {"elapsed_seconds", "setup_seconds", "simulation_seconds", "process_cpu_seconds"}
        assert [{k: v for k, v in row.items() if k not in excluded} for row in results] == [{k: v for k, v in row.items() if k not in excluded} for row in reference]
    count += len(results)
    print(json.dumps({"mode": mode, "width": width, "completed": len(results)}), flush=True)
if mode == "benchmark":
    subprocess.run([sys.executable, str(root / "audit_benchmark.py"), str(output), str(output / "audit.json")], check=True, timeout=300)
assert count == (48 if mode == "qualification" else 18639)
(output / "complete.json").write_text(json.dumps({"mode": mode, "exit_code": 0, "native_runs": count,
    "payload_manifest_sha256": hashlib.sha256((root / "payload-sha256.json").read_bytes()).hexdigest()}, indent=2) + "\n")
archive = root / (mode + ".tar.gz")
with tarfile.open(archive, "x:gz") as bundle:
    bundle.add(output, arcname=mode)
print(json.dumps({"archive": str(archive), "bytes": archive.stat().st_size, "sha256": hashlib.sha256(archive.read_bytes()).hexdigest()}), flush=True)
