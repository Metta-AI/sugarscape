"""Audit all four complete shards for one declared ranking model."""

import argparse
import gzip
import hashlib
import json
from pathlib import Path
import random
from typing import Literal

import numpy as np
from pydantic import BaseModel, ConfigDict, Field


class Request(BaseModel):
    model_config = ConfigDict(extra="forbid")
    id: int = Field(ge=0)
    seed: int = Field(ge=1)
    phase: Literal[0, 4]
    clipped: Literal[False]
    policy: list[Literal[0.0, 0.25, 0.5, 0.75]] = Field(min_length=200, max_length=200)


class Result(BaseModel):
    model_config = ConfigDict(extra="forbid")
    id: int = Field(ge=0)
    seed: int = Field(ge=1)
    phase: Literal[0, 4]
    clipped: Literal[False]
    steps: Literal[50]
    population: int = Field(ge=0, le=200)
    total_tax: int
    debt_refund: int = Field(ge=0, le=8000)
    state_sha256: str = Field(pattern="^[a-f0-9]{64}$")
    elapsed_seconds: float = Field(gt=0, allow_inf_nan=False)


parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("experiment", type=Path)
parser.add_argument("model")
parser.add_argument("output", type=Path)
parser.add_argument(
    "--seed-design", choices=["common", "independent"], default="common"
)
parser.add_argument(
    "--death-boundary", choices=["nonpositive", "negative"], default="nonpositive"
)
args = parser.parse_args()
root = args.experiment
run = root / "execution"
protocol = json.loads((root / "protocol.json").read_text())
manifest = json.loads((run / "manifest.json").read_text())
assert (
    hashlib.sha256((root / "protocol.json").read_bytes()).hexdigest()
    == manifest["sha256"]["protocol.json"]
)
assert (
    hashlib.sha256((root / "policies.json").read_bytes()).hexdigest()
    == protocol["policies_sha256"]
)
assert (
    hashlib.sha256((root / "reduction-protocol.json").read_bytes()).hexdigest()
    == protocol["reduction_protocol_sha256"]
)
policies = json.loads((root / "policies.json").read_text())
assert len(policies) == 100
for name in ["RunPolicyBatch.java", "RunPolicyBatch.class", "run_rankings.py"]:
    assert (
        hashlib.sha256((run / name).read_bytes()).hexdigest()
        == manifest["sha256"][name]
    )
# Retained experiments use either of two independently qualified evaluator revisions.
references = [
    json.loads((Path(__file__).parent / "results" / name / "manifest.json").read_text())
    for name in ["batch-evaluator-2026-10-18", "headless-batch-evaluator-2026-10-18"]
]
reference = {item["source_sha256"]: item for item in references}[
    manifest["sha256"]["RunPolicyBatch.java"]
]
assert manifest["jars"] == reference["jars"]
assert (
    json.loads((run / "pipeline-audit.json").read_text())[
        "exact_complete_native_reference_matches"
    ]
    == 400
)
jobs = [job for job in protocol["jobs"] if job["model"] == args.model]
assert len(jobs) == 4 and {job["shard"] for job in jobs} == set(range(4))
width = jobs[0]["width"]
n = jobs[0]["seeds_per_policy_phase"]
population = 200 * width * width // 2500
refund_bound = (3 if args.death_boundary == "nonpositive" else 40) * population
seed_offset = 100 if width == 50 else 0
first_id = jobs[0]["first_model_id"]
if args.seed_design == "independent":
    generation = protocol["seed_generation"]
    assert generation["method"] == "sample without replacement"
    assert generation["unique_seeds"] == protocol["native_runs"] == 37600
    assert generation["python_random_seed"] == 20261018
    assert (
        generation["range_start_inclusive"],
        generation["range_stop_exclusive"],
    ) == (10000000, 2147483647)
    independent_seeds = random.Random(20261018).sample(
        range(10000000, 2147483647), 37600
    )
    assert len(set(independent_seeds)) == 37600
    seed_values = independent_seeds[first_id : first_id + 200 * n]
else:
    seed_values = list(range(seed_offset + 1, seed_offset + n + 1))
values = np.full((100, 2, n, 3), -1, dtype=np.int64)
seen = np.zeros((100, 2, n), dtype=np.bool_)
file_hashes = {}
for job in jobs:
    assert (job["width"], job["seeds_per_policy_phase"], job["first_model_id"]) == (
        width,
        n,
        first_id,
    )
    model = root / job["model"] / "oremland.nlogo"
    assert hashlib.sha256(model.read_bytes()).hexdigest() == job["model_sha256"]
    death_rule = "sugar <= 0" if args.death_boundary == "nonpositive" else "sugar < 0"
    assert model.read_text().count("ask turtles with [" + death_rule + "] [die]") == 1
    assert (
        hashlib.sha256(model.with_name("sugar-map.txt").read_bytes()).hexdigest()
        == job["landscape_sha256"]
    )
    name = job["model"] + "-shard-" + str(job["shard"])
    terminal = json.loads((run / (name + ".exit.json")).read_text())
    assert terminal["exit_code"] == terminal["decompress_exit_code"] == 0
    inputs = root / job["requests"]
    outputs = run / (name + ".results.jsonl")
    assert hashlib.sha256(inputs.read_bytes()).hexdigest() == job["requests_gz_sha256"]
    digest = hashlib.sha256()
    output_digest = hashlib.sha256()
    count = 0
    with gzip.open(inputs, "rb") as incoming, outputs.open("rb") as outgoing:
        for input_line, output_line in zip(incoming, outgoing, strict=True):
            digest.update(input_line)
            output_digest.update(output_line)
            request = Request.model_validate_json(input_line)
            result = Result.model_validate_json(output_line)
            assert (request.id, request.seed, request.phase) == (
                result.id,
                result.seed,
                result.phase,
            )
            assert request.id % 4 == job["shard"]
            offset = request.id - first_id
            assert 0 <= offset < 200 * n
            policy_id, remainder = divmod(offset, 2 * n)
            phase_index, seed_index = divmod(remainder, n)
            expected_seed = (
                independent_seeds[request.id]
                if args.seed_design == "independent"
                else seed_offset + seed_index + 1
            )
            assert result.seed == expected_seed and result.phase == [0, 4][phase_index]
            assert not seen[policy_id, phase_index, seed_index]
            assert policies[policy_id]["id"] == policy_id
            assert request.policy == [
                quarter / 4 for quarter in policies[policy_id]["quarter_units"]
            ]
            assert (
                0 <= result.population <= population
                and 0 <= result.debt_refund <= refund_bound
            )
            assert result.total_tax + result.debt_refund >= 0
            values[policy_id, phase_index, seed_index] = [
                population - result.population,
                result.total_tax,
                result.total_tax + result.debt_refund,
            ]
            seen[policy_id, phase_index, seed_index] = True
            count += 1
    assert count == job["request_count"]
    assert digest.hexdigest() == job["expanded_requests_sha256"]
    file_hashes[str(outputs.relative_to(root))] = output_digest.hexdigest()
    file_hashes[str(inputs.relative_to(root))] = job["requests_gz_sha256"]
assert seen.all() and int(seen.sum()) == 200 * n
args.output.mkdir(parents=True, exist_ok=False)
(args.output / "policies.json").write_bytes((root / "policies.json").read_bytes())
np.savez_compressed(args.output / "objectives.npz", objectives=values)
with np.load(args.output / "objectives.npz") as restored:
    assert np.array_equal(restored["objectives"], values)
report = {
    "model": args.model,
    "width": width,
    "initial_population": population,
    "policies": 100,
    "clock_phases": [0, 4],
    "seeds_per_policy_phase": n,
    "seed_range": [min(seed_values), max(seed_values)],
    "seed_design": args.seed_design,
    "request_id_range": [first_id, first_id + 200 * n - 1],
    "complete_native_runs": int(seen.sum()),
    "validated_jsonl_lines": 2 * int(seen.sum()),
    "objective_array_shape": list(values.shape),
    "death_boundary": args.death_boundary,
    "objective_order": [
        "deaths",
        "literal_revenue",
        "derived_clipped_revenue"
        if args.death_boundary == "nonpositive"
        else "positive_payments_on_literal_path",
    ],
    "objectives_npz_sha256": hashlib.sha256(
        (args.output / "objectives.npz").read_bytes()
    ).hexdigest(),
    "protocol_sha256": hashlib.sha256(
        (root / "protocol.json").read_bytes()
    ).hexdigest(),
    "policies_sha256": protocol["policies_sha256"],
    "model_sha256": jobs[0]["model_sha256"],
    "landscape_sha256": jobs[0]["landscape_sha256"],
    "file_hashes": file_hashes,
    "scope": "Complete per-model execution audit. This is not a whole-experiment completion claim or a policy-ranking conclusion; other models and scientific analysis remain separate.",
}
(args.output / "audit.json").write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps({key: value for key, value in report.items() if key != "file_hashes"}))
