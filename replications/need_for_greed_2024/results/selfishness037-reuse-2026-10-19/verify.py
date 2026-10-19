"""Read original archives and qualify the shared 100-seed selfishness condition."""

from pathlib import Path
from statistics import median
import hashlib
import json
import math
import sys
import tarfile
import zipfile

workspace, output = map(Path, sys.argv[1:])
assert not output.exists()
repo = workspace / "sugarscape-blueprints"
evidence = workspace / "sugarscape-replication-evidence"
inventory_path = (
    repo
    / "replications/blueprints_2024/results/selfishness037-terminal-prefix-2026-10-19/inventory/inventory.json"
)
inventory_raw = inventory_path.read_bytes()
inventory = json.loads(inventory_raw)
paper_zip = evidence / "papers/need-for-greed.zip"
assert (
    hashlib.sha256(paper_zip.read_bytes()).hexdigest()
    == "e41c89ed31811b2d100c0a54f9c0110f0572a980b599e2417b2653b934fbe440"
)
source_hashes = json.loads(
    (repo / "replications/blueprints_2024/source-sha256.json").read_text()
)["source_sha256"]
with zipfile.ZipFile(paper_zip) as archive:
    expected = {
        name: archive.read(name)
        for name in archive.namelist()
        if name.startswith("0.37-")
    }
assert len(expected) == 100
assert len({json.loads(raw)["seed"] for raw in expected.values()}) == 100
selected = {
    item["entry"]: item
    for item in inventory["excluded_controls"]
    if item["entry"] in expected
}
assert selected.keys() == expected.keys()
archive_hashes = {
    item["native_archive"]: item["native_archive_sha256"]
    for item in inventory["completed_sources"]
}
groups = {}
for entry, item in selected.items():
    source = item["audit_sources"][0]
    assert len(source["manifest_members"]) == 1
    groups.setdefault(source["native_archive"], []).append((entry, item, source))
rows = []
for path, wanted in sorted(groups.items()):
    assert (
        hashlib.sha256((repo / path).read_bytes()).hexdigest() == archive_hashes[path]
    )
    with tarfile.open(repo / path) as archive:
        for entry, item, source in sorted(wanted):
            audit_raw = (repo / source["audit"]).read_bytes()
            assert hashlib.sha256(audit_raw).hexdigest() == source["audit_sha256"]
            audit = json.loads(audit_raw)["validated"]
            prefix = source["manifest_members"][0].rsplit("/", 1)[0]
            original = archive.extractfile(prefix + "/original.config").read()
            assert original == expected[entry]
            config_hash = hashlib.sha256(original).hexdigest()
            assert config_hash == item["configuration_sha256"]
            manifest = json.load(archive.extractfile(prefix + "/manifest.json"))
            assert manifest["entry"] == entry
            assert (
                manifest["release"]
                == inventory["release"]
                == "b9ca671ab7591c7b3606f2d76c33eda344d626d1"
            )
            assert (
                manifest["archive_sha256"] == inventory["archive_sha256"]["selfishness"]
            )
            assert manifest["pythonhashseed"] == "0"
            assert manifest["source_sha256"] == source_hashes
            assert manifest["original_config_sha256"] == config_hash
            assert set(manifest["changes"]) == {"logfile"}
            assert manifest["effective_models_after_native_normalization"] == [
                "benthamHalfLookaheadBinary"
            ]
            config_raw = archive.extractfile(prefix + "/config.json").read()
            assert hashlib.sha256(config_raw).hexdigest() == manifest["config_sha256"]
            config = json.loads(original)
            assert json.loads(config_raw) == config | {
                "logfile": manifest["changes"]["logfile"]["effective"]
            }
            assert config["agentSelfishnessFactor"] == [0.37, 0.37]
            assert config["startingAgents"] == 250 and config["timesteps"] == 5000
            raw = archive.extractfile(prefix + "/trajectory.json").read()
            trajectory_hash = hashlib.sha256(raw).hexdigest()
            assert (
                trajectory_hash
                == item["trajectory_sha256"]
                == audit["trajectory_sha256"]
            )
            records = json.loads(raw)
            assert len(records) == audit["observations"]
            assert records[0]["population"] == 250
            assert records[-1]["population"] == audit["final_population"]
            assert len(records) == 5001 or records[-1]["population"] == 0
            assert config["seed"] == audit["seed"] and audit["entry"] == entry
            for timestep, record in enumerate(records):
                assert record["timestep"] == timestep
                assert all(
                    math.isfinite(v)
                    for v in record.values()
                    if isinstance(v, (int, float))
                )
                assert (
                    int(record["population"]) == record["population"]
                    and 0 <= record["population"] <= 2500
                )
            rows.append(
                {
                    "entry": entry,
                    "seed": config["seed"],
                    "configuration_sha256": config_hash,
                    "trajectory_sha256": trajectory_hash,
                    "observations": len(records),
                    "final_population": records[-1]["population"],
                    "population_sum": sum(record["population"] for record in records),
                    "native_archive": path,
                    "manifest_member": prefix + "/manifest.json",
                }
            )
assert len(rows) == len({r["entry"] for r in rows}) == 100
rows.sort(key=lambda r: r["entry"])
conventions = {}
for exclude_initial in [False, True]:
    for zero_extended in [False, True]:
        name = ("zero_extended" if zero_extended else "observed") + (
            "_excluding_initial" if exclude_initial else "_including_initial"
        )
        values = [
            (r["population_sum"] - 250 * exclude_initial)
            / ((5001 if zero_extended else r["observations"]) - exclude_initial)
            for r in rows
        ]
        conventions[name] = median(values)
dead = sum(r["final_population"] == 0 for r in rows)
equal = sum(r["final_population"] == 250 for r in rows)
worse = sum(0 < r["final_population"] < 250 for r in rows)
better = sum(r["final_population"] > 250 for r in rows)
report = {
    "native_inputs": 100,
    "observations": sum(r["observations"] for r in rows),
    "condition": 0.37,
    "paper_archive_sha256": hashlib.sha256(paper_zip.read_bytes()).hexdigest(),
    "inventory_sha256": hashlib.sha256(inventory_raw).hexdigest(),
    "source_sha256": source_hashes,
    "native_archive_sha256": {path: archive_hashes[path] for path in sorted(groups)},
    "endpoints": {
        "dead": dead,
        "below_initial_nonzero": worse,
        "equal_initial": equal,
        "above_initial": better,
    },
    "population_medians": conventions,
    "runs": rows,
    "scope": "Fresh native archive verification of the exact 100 deposited Need for Greed inputs at selfishness 0.37. No new simulation, baseline substitution, full five-level Table IV bin, paper-curve agreement, or completed-paper claim.",
}
assert dead + worse + equal + better == 100
output.write_text(json.dumps(report, indent=2) + "\n")
print(
    json.dumps(
        {
            k: report[k]
            for k in [
                "native_inputs",
                "observations",
                "endpoints",
                "population_medians",
                "scope",
            ]
        },
        indent=2,
    )
)
