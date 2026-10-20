"""Partition all deposited inputs into audited, reserved, and remaining work."""

from collections import Counter
from pathlib import Path
from typing import Literal
import gzip
import hashlib
import json
import statistics
import sys
import tarfile
import zipfile

from pydantic import BaseModel, ConfigDict


class Input(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    entry: str
    kind: Literal["baseline", "sweep"]
    condition: str
    seed: int
    original_sha256: str
    disposition: Literal["audited", "reserved_control", "remaining"]


workspace, output = map(Path, sys.argv[1:])
assert not output.exists()
evidence = workspace / "sugarscape-replication-evidence"
sources = {
    "baseline": evidence / "need-for-greed-raw-location-001/native-audit.json",
    "sweep": evidence / "need-for-greed-sweep-reuse-001/audit.json",
    "controls": evidence / "need-for-greed-endpoint-qualification-001/protocol.json",
}
baseline, sweep, controls = [json.loads(sources[name].read_bytes()) for name in sources]
audited = {r["entry"] for r in baseline["runs"]} | {r["entry"] for r in sweep["runs"]}
assert len(audited) == 164
reserved = {r["entry"] for r in controls["runs"]}
assert len(reserved) == 6
archive = evidence / "papers/need-for-greed.zip"
archive_sha = hashlib.sha256(archive.read_bytes()).hexdigest()
assert archive_sha == "e41c89ed31811b2d100c0a54f9c0110f0572a980b599e2417b2653b934fbe440"
rows = []
with zipfile.ZipFile(archive) as bundle:
    for name in sorted(bundle.namelist()):
        assert name.endswith(".config")
        raw = bundle.read(name)
        config = json.loads(raw)
        assert config["timesteps"] == 5000 and config["startingAgents"] == 250
        sweep_input = name[0].isdigit()
        if sweep_input:
            condition = name.split("-", 1)[0]
            assert config["agentSelfishnessFactor"] == [float(condition)] * 2
            assert config["agentDecisionModel"] == "benthamHalfLookaheadBinary"
            assert config["agentDecisionModels"] == ["none"]
        else:
            condition = config["agentDecisionModels"][0]
            assert len(config["agentDecisionModels"]) == 1
        rows.append(
            Input(
                entry=name,
                kind="sweep" if sweep_input else "baseline",
                condition=condition,
                seed=config["seed"],
                original_sha256=hashlib.sha256(raw).hexdigest(),
                disposition="audited"
                if name in audited
                else "reserved_control"
                if name in reserved
                else "remaining",
            )
        )
assert len(rows) == len({r.entry for r in rows}) == 10500
assert audited | reserved <= {r.entry for r in rows}
assert Counter(r.kind for r in rows) == {"baseline": 400, "sweep": 10100}
assert len({r.seed for r in rows}) == 100
common_seeds = {r.seed for r in rows}
for kind, condition in {(r.kind, r.condition) for r in rows}:
    cohort = [r for r in rows if r.kind == kind and r.condition == condition]
    assert len(cohort) == 100 and {r.seed for r in cohort} == common_seeds
by_entry = {r.entry: r for r in rows}
for row in sweep["runs"]:
    assert by_entry[row["entry"]].original_sha256 == row["configuration_sha256"]
for row in controls["runs"]:
    assert by_entry[row["entry"]].original_sha256 == row["original_sha256"]
counts = Counter((r.kind, r.disposition) for r in rows)
groups = {}
for row in sweep["runs"]:
    groups.setdefault(row["native_archive"], {})[
        row["manifest_member"].rsplit("/", 1)[0] + "/result.json"
    ] = row
timings = []
for path, wanted in sorted(groups.items()):
    source = workspace / "sugarscape-blueprints" / path
    assert (
        hashlib.sha256(source.read_bytes()).hexdigest()
        == sweep["native_archive_sha256"][path]
    )
    found = set()
    with tarfile.open(source, mode="r|gz") as bundle:
        for member in bundle:
            if member.name not in wanted:
                continue
            assert member.name not in found
            found.add(member.name)
            result = json.load(bundle.extractfile(member))
            expected = wanted[member.name]
            assert (
                result["entry"] == expected["entry"]
                and result["trajectory_sha256"] == expected["trajectory_sha256"]
            )
            assert result["observations"] == expected["observations"]
            timings.append(
                {
                    "entry": result["entry"],
                    "elapsed_seconds": result["elapsed_seconds"],
                    "archive": path,
                    "archive_sha256": sweep["native_archive_sha256"][path],
                }
            )
    assert found == wanted.keys()
assert len(timings) == 100
output.mkdir()
body = json.dumps(
    [r.model_dump() for r in rows], sort_keys=True, separators=(",", ":")
).encode()
(output / "inputs.json.gz").write_bytes(gzip.compress(body, mtime=0))
remaining = sum(r.disposition == "remaining" for r in rows)
mean_seconds = statistics.mean(r["elapsed_seconds"] for r in timings)
report = {
    "paper_archive_sha256": archive_sha,
    "source_sha256": {
        name: hashlib.sha256(path.read_bytes()).hexdigest()
        for name, path in sources.items()
    },
    "partition_counts": {
        kind: {
            status: counts[(kind, status)]
            for status in ["audited", "reserved_control", "remaining"]
        }
        for kind in ["baseline", "sweep"]
    },
    "audited_control_overlap": sorted(audited & reserved),
    "inputs_json_gz_sha256": hashlib.sha256(
        (output / "inputs.json.gz").read_bytes()
    ).hexdigest(),
    "timing_sample": {
        "condition": 0.37,
        "inputs": 100,
        "mean_seconds": mean_seconds,
        "median_seconds": statistics.median(r["elapsed_seconds"] for r in timings),
        "min_seconds": min(r["elapsed_seconds"] for r in timings),
        "max_seconds": max(r["elapsed_seconds"] for r in timings),
    },
    "illustrative_projection": {
        "remaining_inputs": remaining,
        "workers": 8,
        "historical_node_dollars_per_minute": 0.012,
        "hours_at_sample_mean": remaining * mean_seconds / 8 / 3600,
        "compute_dollars_at_sample_mean": remaining * mean_seconds / 8 / 60 * 0.012,
    },
    "scope": "Exact original-input partition; no input or job launched. All control reservations stay excluded regardless of interim completion. Timing projection extrapolates one condition on prior shared hardware and is not a quote, budget, capacity reservation, or launch authorization. Full work needs bounds and a qualified available runtime.",
}
(output / "plan.json").write_text(json.dumps(report, indent=2) + "\n")
(output / "timings.json").write_text(
    json.dumps(sorted(timings, key=lambda r: r["entry"]), indent=2) + "\n"
)
print(json.dumps(report, indent=2))
