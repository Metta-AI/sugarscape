"""Freeze all reduced-policy ranking runs at the paper's maximum simulation budgets."""

import argparse
import gzip
import hashlib
import json
from pathlib import Path

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("models", type=Path)
parser.add_argument("convergence", type=Path)
parser.add_argument("output", type=Path)
args = parser.parse_args()
model_protocol = json.loads((args.models / "protocol.json").read_text())
qualification = json.loads((args.models / "audit.json").read_text())
assert qualification["complete_native_runs"] == 96
assert (
    json.loads((args.convergence / "execution/exit.json").read_text())["exit_codes"]
    == [0] * 4
)
policies = json.loads((args.convergence / "policies.json").read_text())
assert len(policies) == 100
args.output.mkdir(parents=True, exist_ok=False)
(args.output / "policies.json").write_bytes(
    (args.convergence / "policies.json").read_bytes()
)
(args.output / "reduction-protocol.json").write_bytes(
    (args.models / "protocol.json").read_bytes()
)
budgets = {40: 88, 30: 173, 20: 427, 10: 1375, 5: 3900}
jobs = []
request_id = 0
for qualified in qualification["models"]:
    name = qualified["model"]
    model = next(row for row in model_protocol["models"] if row["name"] == name)
    if model["width"] == 50:
        continue
    source = args.models / name
    target = args.output / name
    target.mkdir()
    for filename, digest in [
        ("oremland.nlogo", model["model_sha256"]),
        ("sugar-map.txt", model["landscape_sha256"]),
    ]:
        data = (source / filename).read_bytes()
        assert hashlib.sha256(data).hexdigest() == digest
        (target / filename).write_bytes(data)
    streams = [
        gzip.open(target / f"requests-{shard}.jsonl.gz", "xt") for shard in range(4)
    ]
    hashes = [hashlib.sha256() for _ in range(4)]
    counts = [0] * 4
    first_id = request_id
    try:
        for policy in policies:
            rates = [value / 4 for value in policy["quarter_units"]]
            # Only the varying ID/seed/phase fields are serialized for every seed.
            suffix = (
                ',"clipped":false,"policy":'
                + json.dumps(rates, separators=(",", ":"))
                + "}\n"
            )
            for phase in [0, 4]:
                for seed in range(1, budgets[model["width"]] + 1):
                    line = (
                        '{"id":'
                        + str(request_id)
                        + ',"seed":'
                        + str(seed)
                        + ',"phase":'
                        + str(phase)
                        + suffix
                    )
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
                "width": model["width"],
                "shard": shard,
                "requests": str(requests.relative_to(args.output)),
                "request_count": counts[shard],
                "first_model_id": first_id,
                "seeds_per_policy_phase": budgets[model["width"]],
                "expanded_requests_sha256": hashes[shard].hexdigest(),
                "requests_gz_sha256": hashlib.sha256(requests.read_bytes()).hexdigest(),
                "model_sha256": model["model_sha256"],
                "landscape_sha256": model["landscape_sha256"],
            }
        )
protocol = {
    "paper": "https://www.jasss.org/17/2/6.html",
    "target": "Figure 10 policy-ranking comparisons across reduced sizes and Table 2 maximum simulation budgets",
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
    "qualification_audit_sha256": hashlib.sha256(
        (args.models / "audit.json").read_bytes()
    ).hexdigest(),
    "generator_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    "full_size_reference": str(args.convergence.resolve()),
    "full_size_reference_manifest_sha256": hashlib.sha256(
        (args.convergence / "execution/manifest.json").read_bytes()
    ).hexdigest(),
    "analysis_declared_before_execution": [
        "Reuse the qualified full-size convergence results; the 50-seed prefix is the reference budget. Do not duplicate these simulations.",
        "Evaluate every reduced model with the same 100 frozen policies; retain both tax clocks and every distinct reduction sensitivity case.",
        "Use seeds 1..N at each reduced size, with N from Table 2. Smaller runtime-budget comparisons use prefixes; no new runs are needed.",
        "Report raw deaths and literal tax income; clipped tax income remains a separately labeled derived sensitivity measure.",
        "Report linear and quadratic weighted kappa, and rank/tie conventions explicitly. The source does not uniquely specify the weighting or ties.",
        "Preserve all cases and unresolved source assumptions; do not select reduction settings or ranking conventions by resemblance to the published figure.",
        "No paper-completion or validated negative-replication credit follows from these reconstructed ranking results alone; optimization and transfer remain required.",
    ],
    "jobs": jobs,
}
(args.output / "protocol.json").write_text(json.dumps(protocol, indent=2) + "\n")
print(json.dumps({"native_runs": request_id, "jobs": len(jobs)}))
