"""Freeze a post hoc independent-stream diagnostic for the ranking discrepancy."""

import argparse
import gzip
import hashlib
import json
from pathlib import Path
import random

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("models", type=Path)
parser.add_argument("convergence", type=Path)
parser.add_argument("output", type=Path)
args = parser.parse_args()
args.output.mkdir(parents=True, exist_ok=False)
model_protocol = json.loads((args.models / "protocol.json").read_text())
policies = json.loads((args.convergence / "policies.json").read_text())
assert len(policies) == 100
(args.output / "policies.json").write_bytes(
    (args.convergence / "policies.json").read_bytes()
)
(args.output / "reduction-protocol.json").write_bytes(
    (args.models / "protocol.json").read_bytes()
)
seed_values = random.Random(20261018).sample(range(10000000, 2147483647), 37600)
assert len(seed_values) == len(set(seed_values)) == 37600
jobs = []
request_id = 0
for name, source_name, count, role in [
    ("50-independent-reference", "50-pixel_centers-nearest", 50, "reference"),
    (
        "50-independent-comparison",
        "50-pixel_centers-nearest",
        50,
        "full_size_comparison",
    ),
    ("40-independent-comparison", "40-pixel_centers-nearest", 88, "reduced_comparison"),
]:
    model = next(row for row in model_protocol["models"] if row["name"] == source_name)
    target = args.output / name
    target.mkdir()
    for filename, digest in [
        ("oremland.nlogo", model["model_sha256"]),
        ("sugar-map.txt", model["landscape_sha256"]),
    ]:
        content = (args.models / source_name / filename).read_bytes()
        assert hashlib.sha256(content).hexdigest() == digest
        (target / filename).write_bytes(content)
    first_id = request_id
    streams = [
        gzip.open(target / f"requests-{shard}.jsonl.gz", "xt") for shard in range(4)
    ]
    hashes = [hashlib.sha256() for _ in range(4)]
    counts = [0] * 4
    try:
        for policy in policies:
            rates = [value / 4 for value in policy["quarter_units"]]
            for phase in [0, 4]:
                for _ in range(count):
                    row = {
                        "id": request_id,
                        "seed": seed_values[request_id],
                        "phase": phase,
                        "clipped": False,
                        "policy": rates,
                    }
                    line = json.dumps(row, separators=(",", ":")) + "\n"
                    shard = request_id % 4
                    streams[shard].write(line)
                    hashes[shard].update(line.encode())
                    counts[shard] += 1
                    request_id += 1
    finally:
        for stream in streams:
            stream.close()
    for shard in range(4):
        requests = target / f"requests-{shard}.jsonl.gz"
        jobs.append(
            {
                "model": name,
                "source_model": source_name,
                "role": role,
                "width": model["width"],
                "shard": shard,
                "requests": str(requests.relative_to(args.output)),
                "request_count": counts[shard],
                "first_model_id": first_id,
                "seeds_per_policy_phase": count,
                "expanded_requests_sha256": hashes[shard].hexdigest(),
                "requests_gz_sha256": hashlib.sha256(requests.read_bytes()).hexdigest(),
                "model_sha256": model["model_sha256"],
                "landscape_sha256": model["landscape_sha256"],
            }
        )
assert request_id == 37600
protocol = {
    "paper": "https://www.jasss.org/17/2/6.html",
    "target": "Post hoc diagnostic of shared-seed coupling, prompted by the first reconstructed 40x40 ranking mismatch; not a preregistered paper replication.",
    "native_runs": request_id,
    "workers": 4,
    "global_execution_limit_seconds": 3600,
    "per_job_limit_seconds": 1800,
    "java_heap_mib": 512,
    "policies_sha256": hashlib.sha256(
        (args.output / "policies.json").read_bytes()
    ).hexdigest(),
    "reduction_protocol_sha256": hashlib.sha256(
        (args.output / "reduction-protocol.json").read_bytes()
    ).hexdigest(),
    "generator_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    "full_size_reference": str(args.convergence.resolve()),
    "full_size_reference_usage": "Runtime pipeline qualification only. Scientific reference comes from 50-independent-reference in this diagnostic.",
    "seed_generation": {
        "python_random_seed": 20261018,
        "method": "sample without replacement",
        "range_start_inclusive": 10000000,
        "range_stop_exclusive": 2147483647,
        "unique_seeds": len(seed_values),
        "assignment": "Increasing request ID, across reference, full-size comparison and 40x40 comparison; no seed is reused across any policy, phase or run.",
    },
    "analysis_declared_before_execution": [
        "Compare independent 50x50 and 40x40 objectives with the independent 50x50 reference, retaining both clocks, all policies and declared ranking conventions.",
        "Report the same pooled and within-mean-rate strata, average/ordinal ties, linear/quadratic kappa, and 2%/10%/100% budget prefixes with floor/ceiling rounding.",
        "Compare against the earlier shared-seed design; do not overwrite or relabel either experiment.",
        "Independent random initialization streams address one reconstruction choice only. A remaining discrepancy is not, by itself, a validated negative replication.",
    ],
    "jobs": jobs,
}
(args.output / "protocol.json").write_text(json.dumps(protocol, indent=2) + "\n")
print(
    json.dumps(
        {"native_runs": request_id, "unique_seeds": len(seed_values), "jobs": len(jobs)}
    )
)
