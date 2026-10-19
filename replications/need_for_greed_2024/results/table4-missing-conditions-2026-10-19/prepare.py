"""Freeze the four missing Table IV conditions from original deposited inputs."""

from pathlib import Path
import gzip
import hashlib
import json
import shutil
import zipfile

root = Path(__file__).resolve().parent
base = root.parent
prior = base / "blueprints-selfishness037-batch-001"
worklist = base / "need-for-greed-remaining-plan-001/prepared/inputs.json.gz"
assert (
    hashlib.sha256(worklist.read_bytes()).hexdigest()
    == "368c43d13e42bcddc867dfa12acbd57ce73a47d2b333c5978599083410a85b8f"
)
rows = json.loads(gzip.decompress(worklist.read_bytes()))
selected = sorted(
    (
        r
        for r in rows
        if r["kind"] == "sweep" and r["condition"] in {"0.36", "0.38", "0.39", "0.4"}
    ),
    key=lambda r: (float(r["condition"]), r["seed"]),
)
assert len(selected) == 400 and all(r["disposition"] == "remaining" for r in selected)
assert len({r["entry"] for r in selected}) == 400
assert len({r["seed"] for r in selected}) == 100
need = base / "papers/need-for-greed.zip"
blue = base / "papers/blueprints-selfishness.zip"
assert (
    hashlib.sha256(need.read_bytes()).hexdigest()
    == "e41c89ed31811b2d100c0a54f9c0110f0572a980b599e2417b2653b934fbe440"
)
assert (
    hashlib.sha256(blue.read_bytes()).hexdigest()
    == "e2016f36a9728c23cee025d7a2e63cd2feffe4c36fbd62970e3a7792cb4d19e7"
)
(root / "inputs").mkdir()
inputs = []
with zipfile.ZipFile(need) as a, zipfile.ZipFile(blue) as b:
    for row in selected:
        raw = a.read(row["entry"])
        assert raw == b.read(row["entry"])
        assert hashlib.sha256(raw).hexdigest() == row["original_sha256"]
        config = json.loads(raw)
        assert config["timesteps"] == 5000 and config["startingAgents"] == 250
        assert config["seed"] == row["seed"]
        (root / "inputs" / row["entry"]).write_bytes(raw)
        inputs.append(
            {
                "experiment": "selfishness",
                "condition": row["condition"],
                "seed": str(row["seed"]),
                "entry": row["entry"],
                "configuration_sha256": row["original_sha256"],
            }
        )
plan = json.loads((prior / "protocol.json").read_text())
for key in ["condition", "already_completed_entry"]:
    del plan[key]
plan.update(
    inputs=inputs,
    conditions=["0.36", "0.38", "0.39", "0.4"],
    remaining_worklist_sha256=hashlib.sha256(worklist.read_bytes()).hexdigest(),
    need_for_greed_archive_sha256=hashlib.sha256(need.read_bytes()).hexdigest(),
    pilot_entries=[inputs[0]["entry"], inputs[300]["entry"]],
    global_simulation_seconds=30600,
    outer_minutes=540,
    estimated_maximum_compute_and_idle_usd=7.02,
    scope="400 original Need for Greed inputs for the four missing conditions in TableIV bin0.36-0.40. Every configuration exactly matches the deposited Blueprints archive used by the qualified native runner. The100 original .37 inputs are already audited and excluded. No whole-paper completion credit.",
    pilot_gate="Two smallest-seed original configurations at .36 and .40 must pass full CPython/PyPy trajectory equality before eight-worker admission. Pilot outputs count once each.",
    admission_budget_note="8.5h simulation budget includes pilot runs;9h outer allows final archival.30min setup/export plus15min idle at0.012USD/min yields7.02USD ceiling; no increase on timeout.",
)
(root / "protocol.json").write_text(json.dumps(plan, indent=2) + "\n")
for name in ["run_supplement.py", "audit_supplement.py", "source-sha256.json"]:
    shutil.copyfile(prior / name, root / name)
script = (prior / "run_supplement_batch.py").read_text().replace("== 34200", "== 30600")
(root / "run_supplement_batch.py").write_text(script)
(root / "preparation.json").write_text(
    json.dumps(
        {
            "inputs": 400,
            "conditions": 4,
            "seeds_per_condition": 100,
            "native_horizon": 5000,
            "all_configs_byte_identical_across_deposits": True,
            "all_inputs_previously_remaining": True,
            "pilot_entries": plan["pilot_entries"],
            "protocol_sha256": hashlib.sha256(
                (root / "protocol.json").read_bytes()
            ).hexdigest(),
            "status": "Prepared, not launched; live runtime, resource, rate, disk and duplicate-work preflight required.",
        },
        indent=2,
    )
    + "\n"
)
print((root / "preparation.json").read_text())
