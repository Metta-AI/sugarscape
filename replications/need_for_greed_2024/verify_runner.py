"""Exercise success, timeout, and duplicate-output behavior through the real CLI."""

from pathlib import Path
import hashlib
import json
import subprocess
import sys

workspace, output = map(Path, sys.argv[1:])
output.mkdir(parents=True, exist_ok=False)
runner = Path(__file__).with_name("run_native.py")
base = [
    sys.executable,
    str(runner),
    str(workspace / "sugarscape-dtl-blueprints-reference"),
    str(workspace / "sugarscape-replication-evidence/papers/need-for-greed.zip"),
]
receipts = []
for name, entry, seconds, expected_code in [
    ("baseline", "altruisticHalfLookaheadBinary238165197779399277.config", 3600, 0),
    ("sweep", "0.0-benthamHalfLookaheadBinary238165197779399277.config", 30, 0),
    ("timeout", "benthamHalfLookaheadBinary238165197779399277.config", 1, 124),
]:
    command = base + [entry, str(output / name), "--seconds", str(seconds)]
    process = subprocess.run(command, capture_output=True, text=True, timeout=60)
    (output / (name + ".stdout")).write_text(process.stdout)
    (output / (name + ".stderr")).write_text(process.stderr)
    assert process.returncode == expected_code, process.stderr
    receipts.append({"case": name, "command": command, "exit_code": process.returncode})
    terminal = json.loads((output / name / "terminal.json").read_text())
    assert terminal["exit_code"] == expected_code
    if name == "timeout":
        assert not (output / name / "result.json").exists()
    else:
        result = json.loads((output / name / "result.json").read_text())
        assert result["status"] == "complete" and result["observations"] == 137
        assert (
            result["trajectory_sha256"]
            == "7ce939b1fed518570dfdc8a5351aa15cd775107a9d6ba3ebe06ff63611a6c2d5"
        )
        assert (
            hashlib.sha256((output / name / "trajectory.json").read_bytes()).hexdigest()
            == result["trajectory_sha256"]
        )
assert (output / "baseline/trajectory.json").read_bytes() == (
    output / "sweep/trajectory.json"
).read_bytes()
before = {
    p.name: hashlib.sha256(p.read_bytes()).hexdigest()
    for p in (output / "baseline").iterdir()
}
command = base + [
    "altruisticHalfLookaheadBinary238165197779399277.config",
    str(output / "baseline"),
    "--seconds",
    "30",
]
process = subprocess.run(command, capture_output=True, text=True, timeout=60)
(output / "duplicate.stdout").write_text(process.stdout)
(output / "duplicate.stderr").write_text(process.stderr)
assert process.returncode != 0
assert before == {
    p.name: hashlib.sha256(p.read_bytes()).hexdigest()
    for p in (output / "baseline").iterdir()
}
receipts.append(
    {"case": "duplicate_output", "command": command, "exit_code": process.returncode}
)
report = {
    "real_cli_cases": receipts,
    "runner_sha256": hashlib.sha256(runner.read_bytes()).hexdigest(),
    "baseline_sweep_and_prior_hash_equal": True,
    "duplicate_directory_unchanged": True,
    "timeout_preserves_receipt_without_success": True,
    "scope": "End-to-end native process verification with real deposited full-horizon configurations. No mocks or shortened timestep settings. Does not qualify every interpreter, long-run outcome, or paper result.",
}
(output / "verification.json").write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps(report, indent=2))
