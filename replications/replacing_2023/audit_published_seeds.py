"""Audit every published seed and report extinction at the executed horizon."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import subprocess

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("batch", type=Path)
parser.add_argument("output", type=Path)
args = parser.parse_args()
root = Path(__file__).resolve().parent
manifest = json.loads((args.batch / "manifest.json").read_text())
target_path = root / "published_targets.json"
assert hashlib.sha256(target_path.read_bytes()).hexdigest() == manifest["target_sha256"]
targets = json.loads(target_path.read_text())["table3"]
assert manifest["scenario"] == "disease_basic"
assert manifest["seeds"] == [row["seed"] for row in targets]
assert len(targets) == 20
completed = [json.loads(line) for line in (args.batch / "completed.jsonl").read_text().splitlines()]
assert [r["seed"] for r in completed] == manifest["seeds"], "Incomplete or reordered published-seed batch"
engine = Path(manifest["engine"])
assert subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=engine, text=True).strip() == manifest["revision"]
original_bytes = (engine / "examples/disease_basic.json").read_bytes()
original = json.loads(original_bytes)
rows = []
observations = 0
for completion, target in zip(completed, targets, strict=True):
    seed = target["seed"]
    directory = args.batch / f"seed-{seed}"
    run = json.loads((directory / "manifest.json").read_text())
    assert run["release"] == manifest["revision"]
    assert run["source_config_sha256"] == hashlib.sha256(original_bytes).hexdigest()
    for name, checksum in run["source_sha256"].items():
        assert hashlib.sha256((engine / name).read_bytes()).hexdigest() == checksum
    config_bytes = (directory / "config.json").read_bytes()
    assert hashlib.sha256(config_bytes).hexdigest() == run["config_sha256"]
    config = json.loads(config_bytes)
    expected = dict(original)
    expected.update(seed=seed, timesteps=500, headlessMode=True, debugMode=["none"], logfile=str(directory.resolve() / "trajectory.json"))
    assert config == expected
    assert completion["command"][-3:] == ["disease_basic", str(seed), str(directory.resolve())]
    data = (directory / "trajectory.json").read_bytes()
    result = json.loads((directory / "result.json").read_text())
    assert result == completion["result"]
    assert hashlib.sha256(data).hexdigest() == result["trajectory_sha256"]
    trajectory = json.loads(data)
    assert len(trajectory) == result["observations"]
    assert [r["timestep"] for r in trajectory] == list(range(len(trajectory)))
    assert trajectory[0]["population"] == original["startingAgents"]
    for r in trajectory:
        assert r["seed"] == seed and 0 <= r["population"] <= 2500
        for value in r.values():
            assert all(math.isfinite(v) for v in value) if isinstance(value, list) else math.isfinite(value)
    final = trajectory[-1]
    assert final["timestep"] == 500 or final["population"] == 0
    assert final["population"] == result["final_population"]
    assert final["timestep"] == result["final_timestep"]
    assert min(r["population"] for r in trajectory) == result["minimum_population"]
    assert max(r["population"] for r in trajectory) == result["maximum_population"]
    observations += len(trajectory)
    rows.append({"seed": seed, "published_qualitative_outcome": target["disease_basic"],
                 "extinct_by_executed_horizon": final["population"] == 0,
                 "final_timestep": final["timestep"], "final_population": final["population"],
                 "minimum_population": result["minimum_population"], "trajectory_sha256": result["trajectory_sha256"]})
report = {"revision": manifest["revision"], "runs": len(rows), "observations": observations,
          "extinctions": sum(r["extinct_by_executed_horizon"] for r in rows), "results": rows,
          "limitation": "Released 500-step horizon; the paper's exact figure/seed assessment times and source revision remain unverified. Survival does not establish qualitative similarity, and a horizon mismatch can prevent a negative-replication verdict."}
args.output.mkdir(parents=True, exist_ok=False)
(args.output / "audit.json").write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps(report))
