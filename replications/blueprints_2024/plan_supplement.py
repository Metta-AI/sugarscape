"""Inventory complete original sweeps and exclude independently audited controls."""

import argparse
from collections import defaultdict
import csv
from decimal import Decimal
import gzip
import hashlib
import io
import json
from pathlib import Path, PurePosixPath
import tarfile
from typing import Literal
import zipfile

from pydantic import BaseModel

from run_supplement import ARCHIVE_SHA256, Configuration, RELEASE


class InputRow(BaseModel):
    experiment: Literal["selfishness", "heterogeneous"]
    condition: int
    seed: int
    entry: str
    configuration_sha256: str


parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("archives", type=Path)
parser.add_argument("output", type=Path)
parser.add_argument(
    "--completed-source",
    nargs=2,
    type=Path,
    action="append",
    required=True,
    metavar=("AUDITS", "NATIVE_ARCHIVE"),
    help="Independent per-input audits and their complete native evidence archive; repeat for every completed source",
)
args = parser.parse_args()
excluded = {}
completed_sources = []
for audits, native_archive in args.completed_source:
    paths = sorted(audits.glob("*/audit.json"))
    assert paths
    with tarfile.open(native_archive, "r:gz") as native:
        manifests = defaultdict(list)
        for member in native.getmembers():
            if member.isfile() and PurePosixPath(member.name).name == "manifest.json":
                raw = native.extractfile(member).read()
                manifests[hashlib.sha256(raw).hexdigest()].append((member.name, raw))
        for path in paths:
            audit = json.loads(path.read_bytes())
            result = audit["validated"]
            entry = result["entry"]
            matches = manifests[audit["manifest_sha256"]]
            assert matches, (path, "No byte-matching producer manifest")
            assert 0 <= result["final_timestep"] <= 5000
            assert result["observations"] == result["final_timestep"] + 1
            assert result["final_timestep"] == 5000 or result["final_population"] == 0
            for member_name, manifest_raw in matches:
                manifest = json.loads(manifest_raw)
                assert manifest["release"] == RELEASE
                assert manifest["entry"] == entry
                assert manifest["experiment"] == result["experiment"]
                assert (
                    manifest["archive_sha256"] == ARCHIVE_SHA256[result["experiment"]]
                )
                parent = PurePosixPath(member_name).parent
                trajectory = native.extractfile(str(parent / "trajectory.json")).read()
                assert (
                    hashlib.sha256(trajectory).hexdigest()
                    == result["trajectory_sha256"]
                )
                rows = json.loads(trajectory)
                assert len(rows) == result["observations"]
                assert [row["timestep"] for row in rows] == list(range(len(rows)))
                assert rows[-1]["population"] == result["final_population"]
                raw = native.extractfile(str(parent / "original.config")).read()
                digest = hashlib.sha256(raw).hexdigest()
                assert digest == manifest["original_config_sha256"]
                assert json.loads(raw)["seed"] == result["seed"]
            key = (result["experiment"], entry)
            identity = {
                "configuration_sha256": digest,
                "trajectory_sha256": result["trajectory_sha256"],
            }
            if key in excluded:
                assert all(
                    excluded[key][name] == value for name, value in identity.items()
                )
            else:
                excluded[key] = identity | {"audit_sources": []}
            excluded[key]["audit_sources"].append(
                {
                    "audit": str(path),
                    "audit_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                    "native_archive": str(native_archive),
                    "manifest_members": [name for name, raw in matches],
                }
            )
    completed_sources.append(
        {
            "audit_directory": str(audits),
            "native_archive": str(native_archive),
            "native_archive_sha256": hashlib.sha256(
                native_archive.read_bytes()
            ).hexdigest(),
            "audited_inputs": len(paths),
        }
    )
assert excluded

rows = []
groups = defaultdict(set)
matched = set()
archive_evidence = {}
for experiment, expected_digest in ARCHIVE_SHA256.items():
    path = args.archives / f"blueprints-{experiment}.zip"
    assert hashlib.sha256(path.read_bytes()).hexdigest() == expected_digest
    archive_evidence[experiment] = expected_digest
    varying = {
        "seed",
        "logfile",
        "agentSelfishnessFactor"
        if experiment == "selfishness"
        else "agentDecisionModels",
    }
    with zipfile.ZipFile(path) as archive:
        names = archive.namelist()
        assert (
            len(names)
            == len(set(names))
            == (50500 if experiment == "selfishness" else 49500)
        )
        baseline = json.loads(archive.read(names[0]))
        constants = {k: v for k, v in baseline.items() if k not in varying}
        for name in names:
            raw = archive.read(name)
            config = json.loads(raw)
            validated = Configuration.model_validate(config)
            assert validated.model_dump() == config
            assert {k: v for k, v in config.items() if k not in varying} == constants
            assert config["logfile"] == "./" + name.removesuffix(".config") + ".json"
            if experiment == "selfishness":
                factor = config["agentSelfishnessFactor"]
                condition_decimal = Decimal(str(factor[0])) * 100
                assert condition_decimal == int(condition_decimal)
                condition = int(condition_decimal)
                assert 0 <= condition <= 100 and factor == [factor[0], factor[0]]
                assert config["agentDecisionModels"] == ["none"]
                assert config["agentDecisionModel"] == "benthamHalfLookaheadBinary"
                assert (
                    name
                    == f"{factor[0]}-benthamHalfLookaheadBinary{validated.seed}.config"
                )
            else:
                models = config["agentDecisionModels"]
                condition = models.count("benthamHalfLookaheadBinary")
                assert 1 <= condition <= 99
                assert models == ["benthamHalfLookaheadBinary"] * condition + [
                    "egoisticHalfLookaheadBinary"
                ] * (100 - condition)
                assert (
                    name
                    == f"{condition}-benthamHalfLookaheadBinary-egoisticHalfLookaheadBinary{validated.seed}.config"
                )
            group = groups[(experiment, condition)]
            assert validated.seed not in group
            group.add(validated.seed)
            row = InputRow(
                experiment=experiment,
                condition=condition,
                seed=validated.seed,
                entry=name,
                configuration_sha256=hashlib.sha256(raw).hexdigest(),
            )
            key = (experiment, name)
            if key in excluded:
                assert row.configuration_sha256 == excluded[key]["configuration_sha256"]
                matched.add(key)
            else:
                rows.append(row)
assert matched == set(excluded)
assert len(groups) == 200
seeds = groups[("selfishness", 0)]
assert len(seeds) == 500 and all(group == seeds for group in groups.values())
assert len(rows) == 100000 - len(excluded)
rows.sort(key=lambda row: (row.experiment, row.condition, row.seed))
args.output.mkdir(parents=True, exist_ok=False)
with (args.output / "remaining.csv.gz").open("xb") as target:
    with gzip.GzipFile(fileobj=target, mode="wb", filename="", mtime=0) as compressed:
        with io.TextIOWrapper(compressed, encoding="utf-8", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=list(InputRow.model_fields))
            writer.writeheader()
            writer.writerows(row.model_dump() for row in rows)
report = {
    "release": RELEASE,
    "archive_sha256": archive_evidence,
    "required_inputs": 100000,
    "completed_sources": completed_sources,
    "remaining_inputs": len(rows),
    "shared_seeds": sorted(seeds),
    "conditions": [
        {
            "experiment": experiment,
            "condition": condition,
            "required": len(group),
            "remaining": sum(
                row.experiment == experiment and row.condition == condition
                for row in rows
            ),
        }
        for (experiment, condition), group in sorted(groups.items())
    ],
    "excluded_controls": [
        {"experiment": experiment, "entry": entry, **evidence}
        for (experiment, entry), evidence in sorted(excluded.items())
    ],
    "remaining_csv_gz_sha256": hashlib.sha256(
        (args.output / "remaining.csv.gz").read_bytes()
    ).hexdigest(),
    "planner_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    "scope": "Exact remaining-input inventory after all supplied independently audited inputs; no new simulations or aggregate results. Selfishness condition is hundredths; heterogeneous condition is utilitarian entries in the original 100-entry list. Runtime qualification and bounded capacity planning remain prerequisites to dispatch.",
}
(args.output / "inventory.json").write_text(json.dumps(report, indent=2) + "\n")
print(
    json.dumps(
        {
            "remaining_inputs": len(rows),
            "excluded_controls": len(excluded),
            "conditions": len(groups),
        }
    )
)
