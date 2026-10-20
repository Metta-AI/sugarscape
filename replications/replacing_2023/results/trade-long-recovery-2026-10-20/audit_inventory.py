"""Replay all retained successful native trajectories before recovery interpretation."""
from pathlib import Path
import gzip
import hashlib
import json
import math
import statistics

root = Path(__file__).resolve().parent
base = root.parent.parent
p = json.loads((root / "protocol.json").read_bytes())
qualification = root.parent / "replacing-trade-passive-qualification-001"
q = json.loads((qualification / "audit.json").read_bytes())
assert all(q[k] == v for k, v in p["qualification_required"].items())
inventory = json.loads((root / "inventory.json").read_bytes())
assert hashlib.sha256((root / "inventory.json").read_bytes()).hexdigest() == p["recovery_inventory_sha256"]
completed = inventory["completed"]
lookup = {(r["seed"], r["condition"]): r for r in completed}
assert len(lookup) == len(completed) == 25
conditions = [p["baseline"], *[t["treatment"] for t in p["treatments"]]]
expected = {(seed, name) for seed in p["seeds"] for name in conditions}
assert set(lookup) < expected
assert {(r["seed"], r["condition"]) for r in inventory["remaining"]} == expected - set(lookup)
native_manifest = json.loads((qualification / "manifest.json").read_bytes())
engine = base / "sugarscape-dtl-replacing-reference"
assert all(hashlib.sha256((engine / f).read_bytes()).hexdigest() == digest for f, digest in native_manifest["source_sha256"].items())
measurements = {}
for seed in p["seeds"]:
    for name in conditions:
        if (seed, name) not in lookup:
            continue
        is_qualification = (seed, name) == (14133, "spice_growback")
        run = Path(lookup[seed, name]["directory"])
        assert json.loads((run / "exit.json").read_bytes())["exit_code"] == 0
        manifest = json.loads((run / "manifest.json").read_bytes())
        assert manifest["source_sha256"] == native_manifest["source_sha256"]
        assert manifest["python"] == native_manifest["python"]
        effective = json.loads((run / "effective-config.json").read_bytes())
        assert effective["timesteps"] == 10000 and effective["seed"] == seed
        assert effective["agentReplacements"] == 0
        prior = base / "sugarscape-replacing/replications/replacing_2023/results/trade-lending-paired20-2026-10-15" / f"seed-{seed}" / name
        original = json.loads(gzip.decompress((prior / "config.json.gz").read_bytes()))
        assert all(effective[k] == v for k, v in original.items() if k not in ("timesteps", "logfile", "__README__"))
        prefix = [json.loads(line) for line in (run / "original-schedule.jsonl").read_text().splitlines()]
        assert prefix == json.loads(gzip.decompress((prior / "trajectory.json.gz").read_bytes()))
        raw = (run / "trajectory.json").read_bytes()
        expected_hash = q["native_trajectory_sha256"] if is_qualification else lookup[seed, name]["trajectory_sha256"]
        assert hashlib.sha256(raw).hexdigest() == expected_hash
        rows = json.loads(raw)
        assert [r["timestep"] for r in rows] == list(range(len(rows)))
        assert rows[0]["population"] == original["startingAgents"]
        assert len(rows) == 10001 or rows[-1]["population"] == 0
        assert len(rows) <= 10001
        for record in rows:
            assert record["seed"] == seed and 0 <= record["population"] <= 2500 and int(record["population"]) == record["population"]
            assert all(math.isfinite(x) for value in record.values() for x in (value if isinstance(value, list) else [value]))
        zeros = [r["timestep"] for r in rows if r["population"] == 0]
        assert not zeros or all(r["population"] == 0 for r in rows[zeros[0]:])
        population = [r["population"] for r in rows] + [0] * (10001 - len(rows))
        blocks = [statistics.mean(population[start:start + 1000]) for start in range(1, 10001, 1000)]
        measurements[seed, name] = {"seed": seed, "condition": name, "native_observations": len(rows), "original_schedule_records_exact": len(prefix), "trajectory_sha256": expected_hash, "extinction_steps": zeros[:1], "absorbing_zero_extension_steps": 10001 - len(rows), "consecutive_1000_step_means": blocks, "mean_steps_5001_10000": statistics.mean(population[5001:10001]), "last_block_minus_previous": blocks[-1] - blocks[-2], "last_five_blocks_range": max(blocks[5:]) - min(blocks[5:])}
report = {"inputs": len(measurements), "observations": sum(r["native_observations"] for r in measurements.values()), "all_original_prefix_records_exact": True, "full_trajectory_numeric_audit": True, "inventory_sha256": hashlib.sha256((root / "inventory.json").read_bytes()).hexdigest()}
assert report["inputs"] == 25 and report["observations"] == 250025
(root / "inventory-audit.json").write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps(report))
