"""Validate every batch request/result against complete rich native workflows."""

import argparse
import csv
import gzip
import hashlib
import json
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class Request(BaseModel):
    model_config = ConfigDict(extra="forbid")
    id: int
    seed: int
    phase: Literal[0, 4]
    clipped: bool
    policy: list[Literal[0.0, 0.25, 0.5, 0.75]] = Field(min_length=200, max_length=200)


class Result(BaseModel):
    model_config = ConfigDict(extra="forbid")
    id: int
    seed: int
    phase: Literal[0, 4]
    clipped: bool
    steps: Literal[50]
    population: int = Field(ge=0, le=200)
    total_tax: int
    debt_refund: int = Field(ge=0, le=600)
    state_sha256: str = Field(pattern="^[a-f0-9]{64}$")
    elapsed_seconds: float = Field(gt=0, allow_inf_nan=False)


parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("run", type=Path)
parser.add_argument(
    "reference", type=Path, help="Published heterogeneous result directory"
)
parser.add_argument("output", type=Path)
args = parser.parse_args()
requests = [
    Request.model_validate_json(line)
    for line in (args.run / "requests.jsonl").read_text().splitlines()
]
results = [
    Result.model_validate_json(line)
    for line in (args.run / "results.jsonl").read_text().splitlines()
]
assert len(requests) == len(results) == 400
assert len({request.id for request in requests}) == 400
policy = [
    float(line) for line in (args.reference / "policy.txt").read_text().splitlines()
]
with gzip.open(args.reference / "trajectory.csv.gz", "rt") as stream:
    reference = {
        (int(row["seed"]), int(row["phase"]), row["clipped"] == "true"): row
        for row in csv.DictReader(stream)
        if row["step"] == "50"
    }
assert len(reference) == 400
seen = set()
for request, result in zip(requests, results, strict=True):
    assert request.id == result.id
    assert (request.seed, request.phase, request.clipped) == (
        result.seed,
        result.phase,
        result.clipped,
    )
    assert request.policy == policy
    key = (result.seed, result.phase, result.clipped)
    assert key not in seen
    seen.add(key)
    row = reference[key]
    assert result.state_sha256 == row["state_sha256"]
    assert result.population == float(row["population"])
    assert result.total_tax == float(row["total_tax"])
    assert result.debt_refund == float(row["debt_refund"])
assert seen == set(reference)
manifest = json.loads((args.run / "manifest.json").read_text())
prior_manifest = json.loads((args.reference / "manifest.json").read_text())
assert manifest["model_sha256"] == prior_manifest["model_sha256"]
assert manifest["jars"] == prior_manifest["jars"]
assert (
    hashlib.sha256((args.run / "requests.jsonl").read_bytes()).hexdigest()
    == manifest["requests_sha256"]
)
assert (
    hashlib.sha256((args.run / "RunPolicyBatch.java").read_bytes()).hexdigest()
    == manifest["source_sha256"]
)
terminal = json.loads((args.run / "exit.json").read_text())
assert terminal["exit_code"] == 0
report = {
    "complete_50_step_runs": len(results),
    "exact_final_state_matches": len(results),
    "exact_objective_value_matches": len(results),
    "validated_input_output_jsonl_lines": len(requests) + len(results),
    "elapsed_seconds": terminal["elapsed_seconds"],
    "reference_elapsed_seconds": json.loads((args.reference / "exit.json").read_text())[
        "elapsed_seconds"
    ],
    "sha256": {
        name: hashlib.sha256((args.run / name).read_bytes()).hexdigest()
        for name in [
            "requests.jsonl",
            "results.jsonl",
            "manifest.json",
            "exit.json",
            "RunPolicyBatch.java",
        ]
    },
    "reference_trajectory_gz_sha256": hashlib.sha256(
        (args.reference / "trajectory.csv.gz").read_bytes()
    ).hexdigest(),
    "scope": "Same complete native workflows through a lower-observation batch evaluator. Runtime difference includes observation/export overhead; not a paper timing reproduction or optimizer result.",
}
with args.output.open("x") as stream:
    stream.write(json.dumps(report, indent=2) + "\n")
print(json.dumps({key: value for key, value in report.items() if key != "sha256"}))
