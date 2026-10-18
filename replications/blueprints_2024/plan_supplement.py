"""Inventory complete original sweeps and exclude independently audited controls."""

import argparse
from collections import defaultdict
import csv
from decimal import Decimal
import gzip
import hashlib
import io
import json
from pathlib import Path
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
parser.add_argument(
    "controls", type=Path, help="Extracted complete six-control evidence"
)
parser.add_argument("audits", type=Path, help="Independent per-control audit directory")
parser.add_argument("output", type=Path)
args = parser.parse_args()
excluded = {}
for path in sorted(args.audits.glob("*/audit.json")):
    audit = json.loads(path.read_bytes())
    result = audit["validated"]
    entry = result["entry"]
    run = args.controls / "runs" / Path(entry).stem
    manifest_raw = (run / "manifest.json").read_bytes()
    assert hashlib.sha256(manifest_raw).hexdigest() == audit["manifest_sha256"]
    manifest = json.loads(manifest_raw)
    assert manifest["release"] == RELEASE
    assert manifest["entry"] == entry
    assert manifest["experiment"] == result["experiment"]
    assert manifest["archive_sha256"] == ARCHIVE_SHA256[result["experiment"]]
    assert (
        hashlib.sha256((run / "trajectory.json").read_bytes()).hexdigest()
        == result["trajectory_sha256"]
    )
    assert result["final_timestep"] == 5000 and result["observations"] == 5001
    raw = (run / "original.config").read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    assert digest == manifest["original_config_sha256"]
    assert json.loads(raw)["seed"] == result["seed"]
    key = (result["experiment"], entry)
    assert key not in excluded
    excluded[key] = {
        "configuration_sha256": digest,
        "audit_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "trajectory_sha256": result["trajectory_sha256"],
    }
assert len(excluded) == 6

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
assert len(rows) == 99994
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
    "scope": "Exact unexecuted-input inventory after six independently audited controls; no new simulations or aggregate results. Selfishness condition is hundredths; heterogeneous condition is utilitarian entries in the original 100-entry list. Runtime qualification and bounded capacity planning remain prerequisites to dispatch.",
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
