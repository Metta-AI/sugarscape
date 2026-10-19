"""Summarize population only after all 500 original condition inputs pass audit."""

import argparse
from collections import defaultdict
import csv
from fractions import Fraction
from decimal import Decimal
import hashlib
import json
from pathlib import Path
from statistics import median
import tarfile
import zipfile

from run_supplement import ARCHIVE_SHA256, RELEASE

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("inventory", type=Path)
parser.add_argument("original_archive", type=Path)
parser.add_argument("output", type=Path)
parser.add_argument(
    "--experiment", choices=("selfishness", "heterogeneous"), required=True
)
parser.add_argument("--condition", type=int, choices=range(101), required=True)
args = parser.parse_args()
assert not args.output.exists()
inventory_bytes = args.inventory.read_bytes()
inventory = json.loads(inventory_bytes)
assert inventory["release"] == RELEASE
assert inventory["archive_sha256"][args.experiment] == ARCHIVE_SHA256[args.experiment]
assert (
    hashlib.sha256(args.original_archive.read_bytes()).hexdigest()
    == ARCHIVE_SHA256[args.experiment]
)
expected = {}
with zipfile.ZipFile(args.original_archive) as archive:
    for name in archive.namelist():
        raw = archive.read(name)
        config = json.loads(raw)
        if args.experiment == "selfishness":
            factor = config["agentSelfishnessFactor"]
            assert factor == [factor[0], factor[0]]
            if Decimal(str(factor[0])) * 100 != args.condition:
                continue
            assert config["agentDecisionModel"] == "benthamHalfLookaheadBinary"
        else:
            models = config["agentDecisionModels"]
            assert len(models) == 100
            count = models.count("benthamHalfLookaheadBinary")
            assert models == ["benthamHalfLookaheadBinary"] * count + [
                "egoisticHalfLookaheadBinary"
            ] * (100 - count)
            if count != args.condition:
                continue
        assert config["startingAgents"] == 250 and config["timesteps"] == 5000
        expected[name] = (config["seed"], hashlib.sha256(raw).hexdigest())
assert len(expected) == len({v[0] for v in expected.values()}) == 500
selected = [
    r
    for r in inventory["excluded_controls"]
    if r["experiment"] == args.experiment and r["entry"] in expected
]
assert len(selected) == len({r["entry"] for r in selected})
assert {r["entry"] for r in selected} == expected.keys(), {
    "validated_inputs": len(selected),
    "required_inputs": 500,
}
assert len(selected) == 500
archives = {
    r["native_archive"]: r["native_archive_sha256"]
    for r in inventory["completed_sources"]
}
groups = defaultdict(dict)
for item in selected:
    seed, config_hash = expected[item["entry"]]
    assert item["configuration_sha256"] == config_hash
    source = item["audit_sources"][0]
    audit_bytes = Path(source["audit"]).read_bytes()
    assert hashlib.sha256(audit_bytes).hexdigest() == source["audit_sha256"]
    audit = json.loads(audit_bytes)["validated"]
    assert audit["entry"] == item["entry"] and audit["seed"] == seed
    assert audit["experiment"] == args.experiment
    assert audit["trajectory_sha256"] == item["trajectory_sha256"]
    assert len(source["manifest_members"]) == 1
    member = str(Path(source["manifest_members"][0]).with_name("trajectory.json"))
    assert member not in groups[source["native_archive"]]
    groups[source["native_archive"]][member] = audit
rows = []
for path, wanted in sorted(groups.items()):
    assert hashlib.sha256(Path(path).read_bytes()).hexdigest() == archives[path]
    seen = set()
    with tarfile.open(path, mode="r|gz") as archive:
        for member in archive:
            if member.name not in wanted:
                continue
            assert member.isfile() and member.name not in seen
            seen.add(member.name)
            raw = archive.extractfile(member).read()
            audit = wanted[member.name]
            assert hashlib.sha256(raw).hexdigest() == audit["trajectory_sha256"]
            trajectory = json.loads(raw)
            assert len(trajectory) == audit["observations"]
            assert [r["timestep"] for r in trajectory] == list(range(len(trajectory)))
            populations = [r["population"] for r in trajectory]
            assert populations[0] == 250
            assert all(int(p) == p and 0 <= p <= 2500 for p in populations)
            assert populations[-1] == audit["final_population"]
            assert len(populations) == 5001 or populations[-1] == 0
            assert len(populations) > 1
            rows.append(
                {
                    "entry": audit["entry"],
                    "seed": audit["seed"],
                    "observations": len(populations),
                    "population_sum": int(sum(populations)),
                    "final_population": populations[-1],
                    "trajectory_sha256": audit["trajectory_sha256"],
                }
            )
    assert seen == wanted.keys()
assert len(rows) == len(selected)
rows.sort(key=lambda r: r["entry"])
assert len(rows) == 500
conventions = {}
for name in [
    "observed_including_initial",
    "observed_excluding_initial",
    "zero_extended_including_initial",
    "zero_extended_excluding_initial",
]:
    exclude_initial = name.endswith("excluding_initial")
    fixed_horizon = name.startswith("zero_extended")
    values = [
        Fraction(
            r["population_sum"] - (250 if exclude_initial else 0),
            (5001 if fixed_horizon else r["observations"]) - int(exclude_initial),
        )
        for r in rows
    ]
    result = median(values)
    ordered = sorted(values)
    assert result == (ordered[249] + ordered[250]) / 2
    conventions[name] = {"median": float(result), "median_exact": str(result)}
report = {
    "experiment": args.experiment,
    "condition": args.condition,
    "source_archive_sha256": ARCHIVE_SHA256[args.experiment],
    "median_definition": "Arithmetic mean of the 250th and 251st ordered per-run means; historical quantile implementation remains unverified.",
    "validated_inputs": len(rows),
    "native_extinctions": sum(r["final_population"] == 0 for r in rows),
    "observations": sum(r["observations"] for r in rows),
    "inventory_sha256": hashlib.sha256(inventory_bytes).hexdigest(),
    "native_archive_sha256": {p: archives[p] for p in sorted(groups)},
    "conventions": conventions,
    "scope": "Complete 500-input population medians under four explicit averaging conventions. Historical conventions and other windows remain unresolved. No confidence intervals, equivalence, full-sweep or paper-completion claim. Zero extension assumes population remains zero after native extinction.",
}
args.output.mkdir(parents=True)
with (args.output / "per-run.csv").open("w") as stream:
    writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
    writer.writeheader()
    writer.writerows(rows)
(args.output / "summary.json").write_text(json.dumps(report, indent=2) + "\n")
print(
    json.dumps(
        {k: v for k, v in report.items() if k != "native_archive_sha256"}, indent=2
    )
)
