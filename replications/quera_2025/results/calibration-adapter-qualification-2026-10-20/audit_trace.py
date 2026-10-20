"""Audit full native loss/gradient traces for stochastic value/Jacobian pairing."""

from pathlib import Path
import csv
import hashlib
import json
import sys

root, trace, output = map(Path, sys.argv[1:])
assert not output.exists()
control = root / "qualification-two-channel-runtime-python"
parity_files = [
    "seed-0-agents.csv",
    "seed-0-cells.csv",
    "wealth.csv",
    "loss-and-gradient.csv",
    "native-jacobians.csv",
]
for name in parity_files:
    assert (trace / name).read_bytes() == (control / name).read_bytes()
for name in ["seed-0-agents.csv", "seed-0-cells.csv"]:
    assert (trace / name).read_bytes() == (root / "reference" / name).read_bytes()
with (trace / "native-jacobians.csv").open() as f:
    native = list(csv.DictReader(f))
parameters = ["p1", "p6", "m_alpha", "m_beta", "w_alpha", "w_beta"]
phases = {}
for phase in ["ordinary", "loss-plain", "loss-ad", "jacobian"]:
    paths = sorted(trace.glob(f"*-{phase}-*.csv"))
    expected = (
        ["primal", "primal"]
        if phase in ["ordinary", "loss-plain"]
        else ["primal", "dual", "primal", "dual"]
    )
    assert [p.stem.split("-")[-1] for p in paths] == expected
    records = []
    for path in paths:
        with path.open() as f:
            data = list(csv.DictReader(f))
        assert [(int(r["channel"]), int(r["time"])) for r in data] == [
            (c, t) for t in range(50) for c in [1, 2]
        ]
        records.append(data)
    phases[phase] = records
assert phases["ordinary"] == phases["loss-plain"]
assert phases["loss-ad"] == phases["jacobian"]
assert phases["loss-ad"][0] == phases["ordinary"][0]
pairs = []
for sample in [1, 2]:
    primal, dual = phases["loss-ad"][2 * (sample - 1) : 2 * sample]
    result = [r for r in native if int(r["simulation"]) == sample]
    assert len(result) == 100
    for p, d, r in zip(primal, dual, result, strict=True):
        assert p["value"] == r["value"]
        assert all(d[k] == r[k] for k in parameters)
    different = sum(p["value"] != d["value"] for p, d in zip(primal, dual, strict=True))
    assert different > 0, (
        "Diagnostic must actually expose distinct stochastic trajectories."
    )
    pairs.append(
        {
            "sample": sample,
            "returned_value_matches_primal_call": True,
            "returned_jacobian_matches_separate_dual_call": True,
            "different_primal_dual_channel_values": different,
        }
    )
with (trace / "loss-and-gradient.csv").open() as f:
    (loss,) = list(csv.DictReader(f))
source_audit = json.loads((root / "rng-pairing-source-audit.json").read_bytes())
for file in source_audit["files"]:
    assert hashlib.sha256(Path(file["path"]).read_bytes()).hexdigest() == file["sha256"]
report = {
    "passive_native_outputs_byte_identical": parity_files,
    "prior_seed0_parity": True,
    "calls": {phase: len(rows) for phase, rows in phases.items()},
    "pairs": pairs,
    "ordinary_loss": float(loss["native_loss"]),
    "differentiated_loss": float(loss["ad_loss"]),
    "native_jacobian_values_matched_to_dual_calls": 1200,
    "source_versions": [
        source_audit["prior_interface_version"],
        source_audit["coupled_interface_version"],
    ],
    "calibration_gate_passed": False,
    "scope": "Full native workflow confirms values and Jacobians originate from different stochastic simulator calls in the author adapter. This diagnoses an implementation issue; posterior impact and a corrected adapter still require validation. No paper-level negative or completion credit.",
    "sha256": {
        p.name: hashlib.sha256(p.read_bytes()).hexdigest()
        for p in sorted(trace.iterdir())
        if p.is_file()
    },
}
output.write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps({k: v for k, v in report.items() if k != "sha256"}))
