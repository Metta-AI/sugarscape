"""Verify pinned native binaries against complete retained culture trajectories."""

import hashlib
import json
from pathlib import Path
import subprocess
import time

root = Path(__file__).resolve().parent
protocol = json.loads((root / "protocol.json").read_text())
expected = json.loads((root / "parity-expected.json").read_text())
results = []
for variant, proof in expected.items():
    spec = protocol["variants"][variant]
    native = Path(spec["root"])
    for name, digest in spec["source_sha256"].items():
        assert hashlib.sha256((native / "source" / name).read_bytes()).hexdigest() == digest
    for name, key in [("observe", "binary_sha256"), ("Observe.hs", "observer_sha256")]:
        assert hashlib.sha256((native / name).read_bytes()).hexdigest() == spec[key]
    output = root / "parity" / variant
    output.mkdir(parents=True, exist_ok=False)
    command = [
        str(native / "observe"),
        proof["constructor"],
        str(proof["seed"]),
        str(proof["steps"]),
        str(proof["stride"]),
        str(output / "trajectory"),
    ]
    (output / "command.json").write_text(json.dumps(command) + "\n")
    started = time.monotonic()
    with (output / "stdout.log").open("wb") as stdout, (output / "stderr.log").open("wb") as stderr:
        result = subprocess.run(command, cwd=native, stdout=stdout, stderr=stderr, timeout=900)
    (output / "exit.json").write_text(json.dumps({"exit_code": result.returncode}) + "\n")
    result.check_returncode()
    measured = {name: hashlib.sha256((output / name).read_bytes()).hexdigest() for name in proof["files_sha256"]}
    assert measured == proof["files_sha256"], (variant, measured, proof["files_sha256"])
    results.append(
        {
            "variant": variant,
            "elapsed_seconds": time.monotonic() - started,
            "files_sha256": measured,
            "exact_retained_trajectory_match": True,
        }
    )
    print(json.dumps(results[-1]), flush=True)
(root / "parity-complete.json").write_text(json.dumps(results, indent=2) + "\n")
