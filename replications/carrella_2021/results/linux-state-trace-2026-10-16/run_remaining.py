"""Execute only audited missing Carrella inputs with the frozen independent producer."""

import concurrent.futures
import hashlib
import json
import platform
import subprocess
import threading
import time
from pathlib import Path

root = Path(__file__).resolve().parent
source = Path("/root/sugarscape/carrella-handoff-001")
for name, digest in json.loads((source / "checksums.json").read_text()).items():
    assert hashlib.sha256((source / name).read_bytes()).hexdigest() == digest
plan = json.loads((root / "production-plan.json").read_text())
assert plan["intervals"] == [[631, 2005], [2139, 3503], [3631, 5000]]
chunks = [(start, min(start + 25, stop)) for low, stop in plan["intervals"] for start in range(low, stop, 25)]
assert sum(stop - start for start, stop in chunks) == 4107
(root / "runs").mkdir()
(root / "start.json").write_text(
    json.dumps(
        {
            "unix": time.time(),
            "platform": platform.platform(),
            "machine": platform.machine(),
            "python": platform.python_version(),
            "chunks": chunks,
            "plan_sha256": hashlib.sha256((root / "production-plan.json").read_bytes()).hexdigest(),
            "runner_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        },
        indent=2,
    )
    + "\n"
)
failed = threading.Event()


def run(chunk):
    if failed.is_set():
        return {"interval": chunk, "state": "not_started_after_failure"}
    start, stop = chunk
    output = root / "runs" / f"rows-{start}-{stop}"
    command = [
        "/root/sugarscape/venv/bin/python",
        str(source / "run_independent.py"),
        str(source / "params_sugarscape.csv"),
        str(source / "sugarscape.csv"),
        str(start),
        str(stop),
        str(output),
    ]
    with (root / f"rows-{start}-{stop}.log").open("x") as log:
        result = subprocess.run(command, stdout=log, stderr=subprocess.STDOUT)
    status = {"interval": chunk, "exit_code": result.returncode}
    (root / f"rows-{start}-{stop}-exit.json").write_text(json.dumps(status) + "\n")
    if result.returncode:
        failed.set()
    return status


def stop_on_failure(future):
    if future.exception():
        failed.set()


with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
    futures = []
    for chunk in chunks:
        future = pool.submit(run, chunk)
        future.add_done_callback(stop_on_failure)
        futures.append(future)
    results = [future.result() for future in futures]
(root / "summary.json").write_text(json.dumps(results, indent=2) + "\n")
assert all("exit_code" in r and r["exit_code"] == 0 for r in results)
