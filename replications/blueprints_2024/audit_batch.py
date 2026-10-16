"""Audit complete original-seed intervals and apply the author's outcome rule."""
import argparse
from collections import Counter
import gzip
import hashlib
import json
import math
from pathlib import Path
import zipfile

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("archive", type=Path)
parser.add_argument("batch", type=Path)
parser.add_argument("output", type=Path)
args = parser.parse_args()
manifest = json.loads((args.batch / "manifest.json").read_text())
assert hashlib.sha256(args.archive.read_bytes()).hexdigest() == manifest["archive_sha256"]
records = [json.loads(line) for line in (args.batch / "completed.jsonl").read_text().splitlines()]
assert [r["seed"] for r in records] == manifest["seeds"], "Incomplete seed interval"
with zipfile.ZipFile(args.archive) as archive:
    original = {name: archive.read(name) for name in archive.namelist()}
configs = [json.loads(data) for data in original.values()]
seeds = sorted(c["seed"] for c in configs if c["agentDecisionModels"] == [manifest["model"]])
assert len(seeds) == len(set(seeds)) == 500
assert manifest["seeds"] == seeds[manifest["start"]:manifest["stop"]]
counts = Counter({"dead": 0, "worse": 0, "better_or_equal": 0})
results = []
observations = 0
for record in records:
    seed = record["seed"]
    directory = args.batch / f"seed-{seed}"
    source = json.loads((directory / "manifest.json").read_text())
    assert source["release"] == "b9ca671ab7591c7b3606f2d76c33eda344d626d1"
    entry = f'{manifest["model"]}{seed}.config'
    assert source["entry"] == entry
    assert (directory / "original.config").read_bytes() == original[entry]
    assert hashlib.sha256(original[entry]).hexdigest() == source["original_config_sha256"]
    effective_bytes = (directory / "config.json").read_bytes()
    assert hashlib.sha256(effective_bytes).hexdigest() == source["config_sha256"]
    effective = json.loads(original[entry])
    effective["logfile"] = str(directory.resolve() / "trajectory.json")
    assert json.loads(effective_bytes) == effective
    compressed = (directory / "trajectory.json.gz").read_bytes()
    assert hashlib.sha256(compressed).hexdigest() == record["compressed_sha256"]
    data = gzip.decompress(compressed)
    result = json.loads((directory / "result.json").read_text())
    assert result == record["result"]
    assert hashlib.sha256(data).hexdigest() == result["trajectory_sha256"]
    rows = json.loads(data)
    assert [r["timestep"] for r in rows] == list(range(len(rows)))
    assert rows[0]["population"] == 250
    arrays = {"agentWealths", "agentTimesToLive", "agentTimesToLiveAgeLimited"}
    for row in rows:
        assert row["seed"] == seed and 0 <= row["population"] <= 2500
        assert {k for k, v in row.items() if isinstance(v, list)} == arrays
        assert all(math.isfinite(v) for k, v in row.items() if k not in arrays)
        assert all(math.isfinite(v) for k in arrays for v in row[k])
    final = rows[-1]
    assert final["timestep"] == 5000 or final["population"] == 0
    assert result["observations"] == len(rows)
    assert result["final_timestep"] == final["timestep"] and result["final_population"] == final["population"]
    # Author plots/plot.py counts population equality with the better group.
    outcome = "dead" if final["population"] == 0 else "worse" if final["population"] < rows[0]["population"] else "better_or_equal"
    counts[outcome] += 1
    observations += len(rows)
    results.append({"seed": seed, "outcome": outcome, "final_population": final["population"],
                    "trajectory_sha256": result["trajectory_sha256"], "observations": len(rows)})
report = {"model": manifest["model"], "start": manifest["start"], "stop": manifest["stop"],
          "runs": len(results), "observations": observations, "counts": dict(counts), "results": results,
          "classification_source": "Pinned author plots/plot.py lines 40–43 and 103: zero dead; surviving below initial worse; equality included in better.",
          "scope": "Only this complete seed interval; not a full paper replication unless all required experiments are separately completed."}
args.output.mkdir(parents=True, exist_ok=False)
(args.output / "audit.json").write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps(report))
