"""Reaudit every complete paired native recorder output."""

import hashlib
import json
import math
from pathlib import Path
import sys

root, output = map(Path, sys.argv[1:3])
assert not output.exists()
protocol = json.loads((root / "protocol.json").read_bytes())
timing = {"elapsed_seconds", "setup_seconds", "simulation_seconds", "process_cpu_seconds"}
hashes = {}
for width in protocol["published_widths"]:
    work = root / f"width-{width}"
    requests = [json.loads(line) for line in (work / "requests.jsonl").read_text().splitlines()]
    original = [json.loads(line) for line in (work / "original.jsonl").read_text().splitlines()]
    timed = [json.loads(line) for line in (work / "timed.jsonl").read_text().splitlines()]
    assert len(requests) == len(original) == len(timed) == 8
    expected = [(rate, seed) for rate in [0.0, 0.25, 0.5, 0.75] for seed in [0, 1]]
    for request, left, right, (rate, seed) in zip(
        requests, original, timed, expected, strict=True
    ):
        assert request == {
            "id": f"rate-{rate}-seed-{seed}",
            "seed": seed,
            "phase": 0,
            "clipped": False,
            "policy": [rate] * 200,
        }
        assert {key: value for key, value in left.items() if key not in timing} == {
            key: value for key, value in right.items() if key not in timing
        }
        assert left["id"] == request["id"] and left["steps"] == 50
        assert all(math.isfinite(right[key]) and right[key] > 0 for key in timing)
        assert right["elapsed_seconds"] >= right["setup_seconds"] + right["simulation_seconds"]
    for name in ["requests.jsonl", "original.jsonl", "timed.jsonl"]:
        path = work / name
        hashes[str(path.relative_to(root))] = hashlib.sha256(path.read_bytes()).hexdigest()
result = {
    "paired_inputs": 48,
    "native_executions": 96,
    "all_non_timing_native_output_fields_exact": True,
    "sha256": hashes,
    "scope": "Passive timing recorder parity across complete native workflows. Contended qualification times are not benchmark results.",
}
output.write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps({key: value for key, value in result.items() if key != "sha256"}))
