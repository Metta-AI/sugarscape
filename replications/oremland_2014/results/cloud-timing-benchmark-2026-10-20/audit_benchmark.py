"""Audit every frozen native timing input and summarize all measured blocks."""

import hashlib
import json
import math
from pathlib import Path
import statistics
import sys

root, output = map(Path, sys.argv[1:3])
assert not output.exists()
plan = json.loads((root / "protocol.json").read_bytes())
admission = json.loads((root / "admission.json").read_bytes())
assert admission["protocol_sha256"] == hashlib.sha256(
    (root / "protocol.json").read_bytes()
).hexdigest()
metrics = ["setup_seconds", "simulation_seconds", "process_cpu_seconds", "elapsed_seconds"]
summary = {}
hashes = {}
total = 0
for width in plan["width_order"]:
    work = root / f"width-{width}"
    terminal = json.loads((work / "terminal.json").read_bytes())
    assert terminal["exit_code"] == 0
    requests = [
        json.loads(line) for line in (work / "requests.jsonl").read_text().splitlines()
    ]
    results = [
        json.loads(line) for line in (work / "results.jsonl").read_text().splitlines()
    ]
    count = plan["simulation_counts"][str(width)]
    assert len(requests) == len(results) == 100 + 3 * count == terminal["native_inputs"]
    total += len(results)
    for index, (request, result) in enumerate(zip(requests, results, strict=True)):
        if index < 100:
            identifier, seed = f"warmup-{index}", 1000 + index
        else:
            repeat, offset = divmod(index - 100, count)
            identifier = f"repeat-{repeat}-input-{offset}"
            seed = 20000 + 10000 * repeat + offset
        assert request == {
            "id": identifier,
            "seed": seed,
            "policy": [0.25] * 200,
            "phase": 0,
            "clipped": False,
        }
        assert (result["id"], result["seed"], result["phase"], result["clipped"]) == (
            identifier,
            seed,
            0,
            False,
        )
        assert result["steps"] == 50
        assert result["population"] >= 0 and result["population"].is_integer()
        assert math.isfinite(result["total_tax"]) and math.isfinite(result["debt_refund"])
        assert len(result["state_sha256"]) == 64
        assert all(character in "0123456789abcdef" for character in result["state_sha256"])
        assert all(math.isfinite(result[name]) and result[name] >= 0 for name in metrics)
        assert result["setup_seconds"] > 0 and result["simulation_seconds"] > 0
        assert result["elapsed_seconds"] >= (
            result["setup_seconds"] + result["simulation_seconds"]
        )
    blocks = []
    for repeat in range(3):
        rows = results[100 + repeat * count : 100 + (repeat + 1) * count]
        totals = {name: math.fsum(row[name] for row in rows) for name in metrics}
        totals["setup_plus_simulation_seconds"] = math.fsum(
            row["setup_seconds"] + row["simulation_seconds"] for row in rows
        )
        blocks.append({"repeat": repeat, "simulations": count, **totals})
    measures = [*metrics, "setup_plus_simulation_seconds"]
    summary[str(width)] = {
        "published_simulations": count,
        "published_batch_seconds": plan["published_batch_seconds"][str(width)],
        "measured_simulations": 3 * count,
        "warmup_simulations_excluded_from_summaries": 100,
        "blocks": blocks,
        "median_batch_seconds": {
            name: statistics.median(row[name] for row in blocks) for name in measures
        },
        "batch_min_max_seconds": {
            name: [min(row[name] for row in blocks), max(row[name] for row in blocks)]
            for name in measures
        },
    }
    assert all(value > 0 for value in summary[str(width)]["median_batch_seconds"].values())
    for name in ["requests.jsonl", "results.jsonl", "terminal.json"]:
        path = work / name
        hashes[str(path.relative_to(root))] = hashlib.sha256(path.read_bytes()).hexdigest()
assert total == plan["maximum_native_runs"] == 18639
for width, row in summary.items():
    row["estimated_simulations_in_full50_budget"] = {
        name: summary["50"]["median_batch_seconds"][name]
        / (row["median_batch_seconds"][name] / row["published_simulations"])
        for name in ["simulation_seconds", "setup_plus_simulation_seconds", "process_cpu_seconds"]
    }
report = {
    "native_runs": total,
    "measured_runs": 18039,
    "warmup_runs": 600,
    "widths": summary,
    "sha256": hashes,
    "scope": "All published batch counts executed three times under declared controls on the reconstruction platform. Equivalent counts are throughput estimates, not additionally executed simulations. Setup includes native command compilation/dispatch. Step timing excludes end-state reporters and exports. No historical hardware equivalence or paper verdict is inferred.",
}
output.write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps({key: value for key, value in report.items() if key not in ["widths", "sha256"]}))
