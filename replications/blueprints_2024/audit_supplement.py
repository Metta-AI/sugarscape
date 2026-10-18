"""Independently validate one complete archived supplementary trajectory."""

import argparse
import hashlib
import json
import math
from pathlib import Path
import zipfile

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("archive", type=Path)
parser.add_argument("run", type=Path)
parser.add_argument("output", type=Path)
parser.add_argument(
    "--expected-runtime", choices=["cpython", "pypy"], default="cpython"
)
args = parser.parse_args()
manifest = json.loads((args.run / "manifest.json").read_text())
assert manifest["release"] == "b9ca671ab7591c7b3606f2d76c33eda344d626d1"
pins = json.loads(Path(__file__).with_name("source-sha256.json").read_text())
assert manifest["source_sha256"] == pins["source_sha256"]
assert manifest["pythonhashseed"] == "0"
if args.expected_runtime == "cpython":
    assert manifest["python"].startswith("3.11.14") and "PyPy" not in manifest["python"]
else:
    assert (
        manifest["python"].startswith("3.11.13") and "PyPy 7.3.20" in manifest["python"]
    )
expected_archives = {
    "selfishness": "e2016f36a9728c23cee025d7a2e63cd2feffe4c36fbd62970e3a7792cb4d19e7",
    "heterogeneous": "c37aa109e59ca8b96cd295b7f022d6bf56f413aabbf246ca432ff5d4360de91a",
}
assert (
    hashlib.sha256(args.archive.read_bytes()).hexdigest()
    == manifest["archive_sha256"]
    == expected_archives[manifest["experiment"]]
)
with zipfile.ZipFile(args.archive) as archive:
    original = archive.read(manifest["entry"])
assert original == (args.run / "original.config").read_bytes()
assert hashlib.sha256(original).hexdigest() == manifest["original_config_sha256"]
configuration = json.loads(original)
effective_bytes = (args.run / "config.json").read_bytes()
assert hashlib.sha256(effective_bytes).hexdigest() == manifest["config_sha256"]
effective = json.loads(effective_bytes)
assert set(effective) == set(configuration)
assert {k for k in effective if effective[k] != configuration[k]} == {"logfile"}
assert manifest["changes"] == {
    "logfile": {"original": configuration["logfile"], "effective": effective["logfile"]}
}
assert configuration["timesteps"] == 5000 and configuration["startingAgents"] == 250
if manifest["experiment"] == "selfishness":
    assert configuration["agentDecisionModels"] == ["none"]
    assert configuration["agentDecisionModel"] == "benthamHalfLookaheadBinary"
    assert manifest["effective_models_after_native_normalization"] == [
        configuration["agentDecisionModel"]
    ]
else:
    assert (
        manifest["effective_models_after_native_normalization"]
        == configuration["agentDecisionModels"]
    )
trajectory = args.run / "trajectory.json"
raw = trajectory.read_bytes()
rows = json.loads(raw)
assert 1 <= len(rows) <= 5001
assert [r["timestep"] for r in rows] == list(range(len(rows)))
assert rows[0]["population"] == 250
arrays = {"agentWealths", "agentTimesToLive", "agentTimesToLiveAgeLimited"}
for row in rows:
    assert row["seed"] == configuration["seed"]
    assert (
        0 <= row["population"] <= 2500 and int(row["population"]) == row["population"]
    )
    assert {k for k, v in row.items() if isinstance(v, list)} == arrays
    assert all(math.isfinite(v) for k, v in row.items() if k not in arrays)
    assert all(math.isfinite(v) for k in arrays for v in row[k])
assert rows[-1]["timestep"] == 5000 or rows[-1]["population"] == 0
population = int(rows[-1]["population"])
result = json.loads((args.run / "result.json").read_text())
expected = {
    "entry": manifest["entry"],
    "seed": configuration["seed"],
    "experiment": manifest["experiment"],
    "effective_models": manifest["effective_models_after_native_normalization"],
    "observations": len(rows),
    "final_timestep": int(rows[-1]["timestep"]),
    "final_population": population,
    "outcome": "dead"
    if population == 0
    else "worse"
    if population < 250
    else "better_or_equal",
    "trajectory_sha256": hashlib.sha256(raw).hexdigest(),
}
assert {k: v for k, v in result.items() if k != "elapsed_seconds"} == expected
args.output.mkdir(parents=True, exist_ok=False)
(args.output / "audit.json").write_text(
    json.dumps(
        {
            "validated": expected,
            "manifest_sha256": hashlib.sha256(
                (args.run / "manifest.json").read_bytes()
            ).hexdigest(),
            "scope": "One complete original input and every native trajectory measurement validated. No aggregate sweep or model-correctness verdict.",
        },
        indent=2,
    )
    + "\n"
)
print(json.dumps(expected))
