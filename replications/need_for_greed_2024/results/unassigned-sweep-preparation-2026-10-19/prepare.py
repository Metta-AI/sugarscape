"""Freeze unassigned original sweep inputs without duplicating current work."""

from pathlib import Path
import gzip
import hashlib
import json
import statistics
import subprocess
import zipfile

root = Path(__file__).resolve().parent
base = root.parent
inventory_path = base / "need-for-greed-table4-prefix-005/reconciliation.json"
inputs_path = base / "need-for-greed-remaining-plan-001/prepared/inputs.json.gz"
protocol_path = base / "need-for-greed-table4-batch-002/protocol.json"
inventory = json.loads(inventory_path.read_bytes())
inputs = json.loads(gzip.decompress(inputs_path.read_bytes()))
assert (
    hashlib.sha256(inputs_path.read_bytes()).hexdigest()
    == "368c43d13e42bcddc867dfa12acbd57ce73a47d2b333c5978599083410a85b8f"
)
lookup = {r["entry"]: r for r in inputs}
assert len(lookup) == 10500
completed = {r["entry"] for r in inventory["runs"]}
assert len(completed) == 462
protocol = json.loads(protocol_path.read_bytes())
assigned = {r["entry"] for r in protocol["inputs"]}
assert len(assigned) == 400
sweep = {r["entry"] for r in inputs if r["kind"] == "sweep"}
reserved = assigned - completed
unassigned = sweep - completed - assigned
assert len(reserved) == 273 and len(unassigned) == 9597
assert (sweep & completed).isdisjoint(reserved) and reserved.isdisjoint(unassigned)
assert (sweep & completed) | reserved | unassigned == sweep
paper = base / "papers/need-for-greed.zip"
blueprints = base / "papers/blueprints-selfishness.zip"
assert (
    hashlib.sha256(paper.read_bytes()).hexdigest()
    == "e41c89ed31811b2d100c0a54f9c0110f0572a980b599e2417b2653b934fbe440"
)
assert (
    hashlib.sha256(blueprints.read_bytes()).hexdigest()
    == "e2016f36a9728c23cee025d7a2e63cd2feffe4c36fbd62970e3a7792cb4d19e7"
)
rows = []
with zipfile.ZipFile(paper) as original, zipfile.ZipFile(blueprints) as shared:
    for entry in sorted(unassigned):
        raw = original.read(entry)
        assert raw == shared.read(entry)
        assert hashlib.sha256(raw).hexdigest() == lookup[entry]["original_sha256"]
        config = json.loads(raw)
        assert config["seed"] == lookup[entry]["seed"]
        rows.append(
            {
                "experiment": "selfishness",
                "condition": lookup[entry]["condition"],
                "seed": str(config["seed"]),
                "entry": entry,
                "configuration_sha256": hashlib.sha256(raw).hexdigest(),
            }
        )
shards = [rows[i::19] for i in range(19)]
assert (
    sum(map(len, shards)) == 9597
    and len({r["entry"] for shard in shards for r in shard}) == 9597
)
out = root / "prepared"
out.mkdir()
for i, shard in enumerate(shards):
    (out / f"batch-{i:02d}.json.gz").write_bytes(
        gzip.compress((json.dumps(shard, indent=2) + "\n").encode(), mtime=0)
    )
node = json.loads(
    subprocess.check_output(
        [
            "autor",
            "node",
            "get",
            "relh-sugarscape-selfishness037-cpu8-20261018-v1",
            "--json",
        ]
    )
)
assert node["chip"] == "cpu-8"
rate = node["rate"]["node_per_min_usd_micros"] / 1000000
(root / "observed-rate.json").write_text(
    json.dumps(
        {
            "node": node["name"],
            "chip": node["chip"],
            "rate": node["rate"],
            "scope": "Current task-node rate observation, not a reservation or guarantee for a future allocation.",
        },
        indent=2,
    )
    + "\n"
)
timings = json.loads(
    (base / "need-for-greed-remaining-plan-001/prepared/timings.json").read_bytes()
)
mean = statistics.mean(r["elapsed_seconds"] for r in timings)
plan = {
    "inputs": 9597,
    "audited_sweep_inputs": 230,
    "reserved_unfinished_sweep_inputs": 273,
    "batches": 19,
    "batch_sizes": [len(s) for s in shards],
    "workers_per_batch": 8,
    "maximum_concurrent_batches": 4,
    "per_input_seconds": 1800,
    "batch_admission_seconds": 41400,
    "batch_outer_seconds": 42800,
    "outer_kill_grace_seconds": 30,
    "export_allowance_seconds": 1800,
    "idle_allowance_seconds": 900,
    "conservative_dollars_per_batch": round((42800 + 30 + 1800 + 900) / 60 * rate, 6),
    "proposed_total_cap_dollars": 175,
    "illustrative_mean_seconds": mean,
    "illustrative_node_hours": len(rows) * mean / 8 / 3600,
    "illustrative_compute_dollars": len(rows) * mean / 8 / 60 * rate,
    "initial_qualification_required": True,
    "qualification_within_outer_bound": True,
    "admission_clock_starts_before_setup_and_qualification": True,
    "all_compute_attempts_including_qualification_count_against_cap": True,
    "source_sha256": {
        str(p): hashlib.sha256(p.read_bytes()).hexdigest()
        for p in [inventory_path, inputs_path, protocol_path, paper, blueprints]
    },
    "shards_sha256": {
        p.name: hashlib.sha256(p.read_bytes()).hexdigest()
        for p in sorted(out.iterdir())
    },
    "scope": "Prepared work only. No capacity reserved, node created, or job launched. Existing400-input assignment remains excluded even when its inputs finish. Single-condition timing extrapolation is not a completion guarantee. Global budget must reserve full bounds before each launch and stop with remaining work recorded; no automatic budget extension.",
}
assert plan["conservative_dollars_per_batch"] * 19 < 175
(out / "plan.json").write_text(json.dumps(plan, indent=2) + "\n")
print(
    json.dumps(
        {k: v for k, v in plan.items() if k not in ["source_sha256", "shards_sha256"]}
    )
)
