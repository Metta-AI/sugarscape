"""Freeze the declared 100-policy, 100-seed full-size convergence experiment."""

import argparse
import hashlib
import json
from math import comb
from pathlib import Path
import random
from typing import Literal

from pydantic import BaseModel, Field


class Request(BaseModel):
    id: int
    seed: int = Field(ge=1, le=100)
    phase: Literal[0, 4]
    clipped: Literal[False]
    policy: list[Literal[0.0, 0.25, 0.5, 0.75]] = Field(min_length=200, max_length=200)


parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("output", type=Path)
args = parser.parse_args()
args.output.mkdir(parents=True, exist_ok=False)
counts = [[0] * 601 for _ in range(201)]
counts[0][0] = 1
for length in range(1, 201):
    for total in range(3 * length + 1):
        counts[length][total] = sum(
            counts[length - 1][total - digit] for digit in range(4) if total >= digit
        )
for total in [100, 200, 300]:
    coefficient = sum(
        (-1) ** index * comb(200, index) * comb(total - 4 * index + 199, 199)
        for index in range(total // 4 + 1)
    )
    assert counts[200][total] == coefficient
rng = random.Random(20261019)
policies = []
for quarter_total, number in [(100, 34), (200, 33), (300, 33)]:
    for _ in range(number):
        remaining = quarter_total
        digits = []
        for index in range(200):
            left = 199 - index
            weights = [
                counts[left][remaining - digit]
                if 0 <= remaining - digit <= 3 * left
                else 0
                for digit in range(4)
            ]
            draw = rng.randrange(sum(weights))
            for digit, weight in enumerate(weights):
                if draw < weight:
                    digits.append(digit)
                    remaining -= digit
                    break
                draw -= weight
        assert remaining == 0 and len(digits) == 200 and sum(digits) == quarter_total
        policies.append(
            {
                "id": len(policies),
                "mean_rate": quarter_total / 800,
                "quarter_units": digits,
            }
        )
assert len(policies) == len({tuple(row["quarter_units"]) for row in policies}) == 100
(args.output / "policies.json").write_text(json.dumps(policies, indent=2) + "\n")
streams = [(args.output / f"requests-{worker}.jsonl").open("x") for worker in range(4)]
try:
    request_id = 0
    for policy in policies:
        for phase in [0, 4]:
            for seed in range(1, 101):
                request = Request(
                    id=request_id,
                    seed=seed,
                    phase=phase,
                    clipped=False,
                    policy=[digit / 4 for digit in policy["quarter_units"]],
                )
                streams[request_id % 4].write(request.model_dump_json() + "\n")
                request_id += 1
finally:
    for stream in streams:
        stream.close()
assert request_id == 20000
protocol = {
    "paper_url": "https://www.jasss.org/17/2/6.html",
    "paper_target": "Figure 9 and section 4.22: convergence of mortality and tax-income summaries with repeated simulation",
    "policy_generation_seed": 20261019,
    "policies": 100,
    "mean_rate_counts": {"0.125": 34, "0.25": 33, "0.375": 33},
    "sampling": "Uniform over all 200-entry quarter-rate vectors conditional on exact total 100, 200, or 300 quarter units; dynamic-program completion counts independently checked by inclusion-exclusion coefficients.",
    "assumptions": [
        "The original 100 vectors and their generating distribution are unavailable.",
        "The 34/33/33 allocation and conditional-uniform distribution are declared reconstruction choices, not recovered author settings.",
        "Use the already qualified native 50x50 model; retain both first-tax-step interpretations.",
        "Use common simulation seeds 1..100 across policies. These are reconstructed seeds, not original author random streams.",
    ],
    "clock_phases": [0, 4],
    "initial_population": 200,
    "horizon": 50,
    "runs": request_id,
    "workers": 4,
    "maximum_seconds_per_worker": 1800,
    "heap_mib_per_worker": 512,
    "analysis_declared_before_execution": [
        "Report every policy and both clock phases; do not select favorable curves.",
        "Compute mortality and literal tax-income mean/standard-deviation curves for prefixes 2..100.",
        "Report 50-versus-100 changes and first-half/second-half sampling uncertainty; no post hoc paper-pass threshold.",
        "Derive clipped revenue as literal revenue plus recorded negative-wealth refunds, using the proven fixed-policy survivor invariant; label these as derived outcomes, not additional runs.",
        "Keep population-standard-deviation and sample-standard-deviation conventions distinguishable.",
        "Treat findings as conditional on the declared reconstruction; original Figure 9 curves, reduced-model rankings, and optimization remain separate requirements.",
    ],
    "generator_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    "files_sha256": {
        path.name: hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(args.output.iterdir())
        if path.is_file()
    },
}
(args.output / "protocol.json").write_text(json.dumps(protocol, indent=2) + "\n")
print(json.dumps({"policies": 100, "runs": request_id, "workers": 4}))
